# Home Assistant Add-on: BLE2MQTT

## Configuration

### MQTT

MQTT connection is auto-discovered from Home Assistant. No configuration needed
if you have the Mosquitto addon or any MQTT integration configured.

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `log_level` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `base_topic` | `ble2mqtt` | MQTT topic prefix for all devices |
| `mqtt_prefix` | `b2m_` | Prefix for device names in MQTT |
| `hci_adapter` | `hci0` | Bluetooth adapter to use |
| `legacy_color_mode` | `false` | Set `true` for HA versions before 2024.4 |
| `devices` | `[]` | List of BLE devices (see below) |

### Device configuration

Each device requires at minimum `address` and `type`:

```yaml
devices:
  - address: "AA:BB:CC:DD:EE:FF"
    type: presence
  - address: "11:22:33:44:55:66"
    type: xiaomilywsd
  - address: "AA:BB:CC:DD:EE:00"
    type: redmond_rk_g200
    key: "ffffffffffffffff"
  - address: "AA:BB:CC:DD:EE:01"
    type: mikettle
    product_id: 275
  - address: "AA:BB:CC:DD:EE:02"
    type: ensto_thermostat
    key: "00112233"
  - address: "AA:BB:CC:DD:EE:03"
    type: miflora
    interval: 600
  - address: "AA:BB:CC:DD:EE:04"
    type: xiaomihtv1
    passive: false
```

### Device fields

| Field | Required | Description |
|-------|----------|-------------|
| `address` | yes | BLE MAC address (`XX:XX:XX:XX:XX:XX`) |
| `type` | yes | Device type identifier (see supported types) |
| `friendly_name` | no | Human-readable name |
| `key` | no | Encryption key (required for Redmond, Ensto) |
| `product_id` | no | Product variant (required for Mi Kettle) |
| `interval` | no | Polling interval in seconds |
| `passive` | no | `true` for passive listening, `false` for active connection |
| `threshold` | no | Presence detection timeout in seconds |

### Supported device types

`presence`, `wp6003`, `redmond_rk_g200`, `redmond_rmc_m200`, `mikettle`,
`xiaomihtv1`, `xiaomilywsd`, `xiaomilywsd_atc`, `am43`, `soma_shades`,
`ensto_thermostat`, `atomfast`, `voltage_bm2`, `mclh09`, `miflora`

Full list: [ble2mqtt docs](https://github.com/devbis/ble2mqtt#supported-devices)

## Finding your device addresses

On startup, the addon scans for nearby BLE devices for 10 seconds and logs them
sorted by signal strength:

```
Scanning for nearby BLE devices (10s)...
  60:03:03:94:11:DF   -37 dBm  6003#06003039411DF
  1C:AF:4A:05:D3:D9   -71 dBm  Samsung S93CA 55
  C4:82:E1:8F:F1:4C   -93 dBm  TY
```

Use the MAC address from this list to add devices to your configuration.
Check the addon **Log** tab after each restart to see available devices.

## Vson WP6003 air quality sensor

The WP6003 reports temperature, CO2, TVOC (mg/m3) and HCHO (mg/m3).

```yaml
devices:
  - address: "60:03:03:94:11:DF"
    type: wp6003
    friendly_name: "Air Quality"
```

**Tips:**
- The sensor may report saturated values (tvoc: 9.999, hcho: 1.999, co2: 2000)
  during the first minutes after power-on. Wait a few minutes for readings to
  stabilize.
- WP6003 devices show up in the BLE scan with names starting with `6003#`.

> **Alternative**: For the WP6003 specifically, consider the native integration
> [hass-vson](https://github.com/eigger/hass-vson) which provides auto-discovery
> via BLE without needing an MQTT broker. Install it via HACS.

## Important notes

- **Bluetooth**: On HAOS, the addon uses the host bluetooth via D-Bus.
  No additional configuration is needed.
- **Network mode**: This addon uses host networking for bluetooth access.
- **Encrypted devices**: For Redmond and Ensto devices, you need to obtain the
  encryption key. See the [ble2mqtt documentation](https://github.com/devbis/ble2mqtt).
