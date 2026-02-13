# Home Assistant Add-on: BLE2MQTT

> **DEPRECATED**: This addon is no longer maintained. For the Vson WP6003 air
> quality sensor, use the native custom integration
> [hass-vson](https://github.com/eigger/hass-vson) instead. It provides
> auto-discovery via BLE, native HA entities, and does not require an MQTT broker.
> Install it via HACS.

Bridge Bluetooth Low Energy (BLE) devices to Home Assistant via MQTT.

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]

## About

This add-on runs [ble2mqtt](https://github.com/devbis/ble2mqtt) as a Home Assistant addon.
It connects to BLE devices and publishes their data to MQTT, where Home Assistant
auto-discovers them.

### Supported devices

Xiaomi sensors (MJ_HT_V1, LYWSD02/03), Mi Flora, Mi Kettle, Redmond kettles/cookers,
Ensto thermostats, AM43/Soma blinds, Vson WP6003, Atom Fast dosimeters, BM2 battery
monitors, Govee/RuuviTag/SwitchBot sensors, and any BLE device as presence tracker.

Full list: [ble2mqtt README](https://github.com/devbis/ble2mqtt#supported-devices)

## Local testing (without Home Assistant)

```bash
cp ble2mqtt.json.example ble2mqtt.json
# Edit ble2mqtt.json with your MQTT broker and device addresses

docker compose -f docker-compose.test.yml build
docker compose -f docker-compose.test.yml up
```

Requires: Bluetooth adapter, MQTT broker, and `bluez` stopped on the host.

## Credits

Based on [ble2mqtt](https://github.com/devbis/ble2mqtt) by [devbis](https://github.com/devbis).

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
