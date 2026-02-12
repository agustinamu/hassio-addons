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

## Important notes

- **Bluetooth conflict**: The host bluetooth service (`bluez`) should be stopped,
  as this addon runs its own bluetooth daemon inside the container.
  On HAOS this is handled automatically.
- **Network mode**: This addon uses host networking for bluetooth access.
- **Encrypted devices**: For Redmond and Ensto devices, you need to obtain the
  encryption key. See the [ble2mqtt documentation](https://github.com/devbis/ble2mqtt).
