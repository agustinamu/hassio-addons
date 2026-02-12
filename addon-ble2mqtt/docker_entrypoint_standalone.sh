#!/bin/bash
# ==============================================================================
# BLE2MQTT standalone entrypoint (for testing without Home Assistant)
# Reads config from /etc/ble2mqtt.json (mounted volume)
# ==============================================================================

set -e

CONFIG_FILE="${BLE2MQTT_CONFIG:-/usr/src/app/ble2mqtt.json}"

echo "[INFO]  Running in standalone mode"

if [[ -f "/etc/ble2mqtt.json" ]]; then
    cp /etc/ble2mqtt.json "${CONFIG_FILE}"
    echo "[INFO]  Using config from /etc/ble2mqtt.json"
elif [[ -f "${CONFIG_FILE}" ]]; then
    echo "[INFO]  Using existing config at ${CONFIG_FILE}"
else
    echo "[ERROR] No config file found. Mount one at /etc/ble2mqtt.json"
    exit 1
fi

echo "[INFO]  Config:"
jq '.' "${CONFIG_FILE}"

# If host D-Bus is mounted, use host's bluetoothd (no conflict with host BT).
# Otherwise, start our own (requires: sudo systemctl stop bluetooth on host).
if [[ -d "/var/run/dbus" ]]; then
    echo "[INFO]  Using host bluetooth (D-Bus mounted)"
else
    echo "[INFO]  Starting container bluetoothd (no host D-Bus)"
    /usr/lib/bluetooth/bluetoothd &
    sleep 2
fi

echo "[INFO]  Starting ble2mqtt..."
exec ble2mqtt
