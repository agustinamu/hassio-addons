#!/command/with-contenv bashio
# ==============================================================================
# BLE2MQTT Add-on entrypoint (HA addon mode)
# Reads configuration from Supervisor API, generates ble2mqtt.json, starts app.
# For standalone testing, use: docker_entrypoint_standalone.sh
# ==============================================================================

CONFIG_FILE="${BLE2MQTT_CONFIG:-/usr/src/app/ble2mqtt.json}"

bashio::log.info "Running in Home Assistant addon mode"

# --- MQTT connection (auto-discovered from HA via services: mqtt:need) ---
MQTT_HOST=$(bashio::services mqtt "host")
MQTT_PORT=$(bashio::services mqtt "port")
MQTT_USER=$(bashio::services mqtt "username")
MQTT_PASS=$(bashio::services mqtt "password")
bashio::log.info "MQTT: ${MQTT_HOST}:${MQTT_PORT} (user: ${MQTT_USER})"

# --- Application settings ---
LOG_LEVEL=$(bashio::config 'log_level' 'INFO')
BASE_TOPIC=$(bashio::config 'base_topic' 'ble2mqtt')
MQTT_PREFIX=$(bashio::config 'mqtt_prefix' 'b2m_')
HCI_ADAPTER=$(bashio::config 'hci_adapter' 'hci0')
LEGACY_COLOR=$(bashio::config 'legacy_color_mode' false)

# --- Devices ---
DEVICES_JSON=$(bashio::config 'devices')
# Ensure valid JSON for --argjson parameters
[[ -z "${DEVICES_JSON}" || "${DEVICES_JSON}" == "null" ]] && DEVICES_JSON="[]"
[[ -z "${MQTT_PORT}" ]] && MQTT_PORT=1883
[[ "${LEGACY_COLOR}" != "true" ]] && LEGACY_COLOR="false"

# --- Build config file with jq ---
jq -n \
    --arg host "${MQTT_HOST}" \
    --argjson port "${MQTT_PORT}" \
    --arg user "${MQTT_USER}" \
    --arg pass "${MQTT_PASS}" \
    --arg log "${LOG_LEVEL}" \
    --arg topic "${BASE_TOPIC}" \
    --arg prefix "${MQTT_PREFIX}" \
    --arg hci "${HCI_ADAPTER}" \
    --argjson legacy "${LEGACY_COLOR}" \
    --argjson devices "${DEVICES_JSON}" \
    '{
        mqtt_host: $host,
        mqtt_port: $port,
        mqtt_user: $user,
        mqtt_password: $pass,
        log_level: $log,
        base_topic: $topic,
        mqtt_prefix: $prefix,
        hci_adapter: $hci,
        legacy_color_mode: $legacy,
        devices: $devices
    }' > "${CONFIG_FILE}"

bashio::log.info "Generated config:"
jq '.mqtt_password = "********"' "${CONFIG_FILE}"

# --- Start bluetooth ---
# If host D-Bus is available (host_dbus: true in config.yaml), use the host's
# bluetoothd. This allows coexistence with other HA bluetooth integrations.
# Otherwise, start our own bluetoothd (requires exclusive BT adapter access).
if [[ -d "/var/run/dbus" ]]; then
    bashio::log.info "Using host bluetooth (D-Bus detected)"
else
    bashio::log.info "Starting container bluetoothd (no host D-Bus)"
    /usr/lib/bluetooth/bluetoothd &
    sleep 2
fi

# --- List available adapters for diagnostics ---
bashio::log.info "Bluetooth adapters:"
bluetoothctl list 2>/dev/null | awk '{printf "  hci%d: %s\n", NR-1, $0}' || echo "  (none found)"

# --- BLE device scan (helps discover MAC addresses for configuration) ---
bashio::log.info "Scanning for nearby BLE devices (10s)..."
python3 -c "
import asyncio
from bleak import BleakScanner

async def scan():
    devices = await BleakScanner.discover(timeout=10, adapter='${HCI_ADAPTER}')
    if not devices:
        print('  (no devices found)')
        return
    for d in sorted(devices, key=lambda x: x.rssi or -999, reverse=True):
        name = d.name or 'Unknown'
        print(f'  {d.address}  {d.rssi:>4} dBm  {name}')

asyncio.run(scan())
" 2>/dev/null || bashio::log.warning "BLE scan failed (non-fatal)"

bashio::log.info "Starting ble2mqtt..."
exec ble2mqtt
