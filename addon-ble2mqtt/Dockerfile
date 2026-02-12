ARG BUILD_FROM=python:3.13-alpine3.21
FROM ${BUILD_FROM}

ENV LANG=C.UTF-8

# Install bash (not present in python:alpine, already in HA base images)
RUN apk add --no-cache bash

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install bluetooth stack and ble2mqtt
RUN apk add --no-cache \
        bluez \
        jq \
    && pip3 install --no-cache-dir --break-system-packages \
        --root-user-action=ignore \
        "ble2mqtt[full]==0.2.5"

# Wrapper: ble2mqtt calls 'hciconfig' which is deprecated and removed from
# modern bluez. This shim translates hciconfig up/down to bluetoothctl.
COPY rootfs /

WORKDIR /usr/src/app

COPY docker_entrypoint.sh docker_entrypoint_standalone.sh /usr/src/app/
RUN chmod +x /usr/src/app/docker_entrypoint.sh /usr/src/app/docker_entrypoint_standalone.sh

ENV BLE2MQTT_CONFIG=/usr/src/app/ble2mqtt.json

CMD [ "/usr/src/app/docker_entrypoint.sh" ]
