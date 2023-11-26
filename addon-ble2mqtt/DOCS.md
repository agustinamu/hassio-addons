# Home Assistant Add-on: addon-ble2mqtt
## How to use

1. In the configuration section, configure at least one device. You can paste the list in json format, when saving it is adapted to yaml. Example yaml:
```yaml
- address: 11:22:33:aa:cc:aa
  type: wp6003
- address: 11:22:33:aa:cc:aa
  type: presence
- address: 11:22:33:aa:bb:cc
  type: redmond_rk_g200
  key: ffffffffffffffff
- address: 11:22:33:aa:bb:c0
  type: redmond_rmc_m200
  key: ffffffffffffffff
- address: 11:22:33:aa:bb:c1
  type: ensto_thermostat
  key: "00112233"
- address: 11:22:33:aa:bb:cd
  type: mikettle
  product_id: 275
- address: 11:22:33:aa:bb:de
  type: am43
- address: 11:22:33:aa:bb:dd
  type: xiaomihtv1
- address: 11:22:34:aa:bb:dd
  type: xiaomihtv1
  passive: false
- address: 11:22:33:aa:bb:ee
  type: xiaomilywsd
- address: 11:22:33:aa:bb:ff
  type: xiaomilywsd_atc
- address: 11:22:33:aa:aa:aa
  type: atomfast
- address: 11:22:33:aa:aa:bb
  type: voltage_bm2
- address: 11:22:33:aa:aa:bc
  type: mclh09
  interval: 600
- address: 11:22:33:aa:aa:bd
  type: miflora
  interval: 500
```

More info in ble2mqtt repo, [url](https://github.com/devbis/ble2mqtt)

2. Save the configuration.
3. Start the add-on.
4. Check the add-on log output to see the result.