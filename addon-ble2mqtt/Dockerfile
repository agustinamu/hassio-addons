ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install requirements for add-on
RUN \
    apk add --no-cache bluez openrc\
    && apk add --no-cache \
         python3 \
             py3-pip \
             bluez\
     \
     && pip3 install bleak>=0.12.0 \
     && pip3 install aio-mqtt-mod>=0.2.0 \
     && pip3 install -U ble2mqtt


# Copy data for add-on


WORKDIR /usr/src/app

# To speed up consecutive builds, copy only requirements and install them
COPY ./ble2mqtt .

COPY ./docker_entrypoint.sh docker_entrypoint.sh
RUN chmod +x docker_entrypoint.sh

ENV BLE2MQTT_CONFIG=/usr/src/app/ble2mqtt.json

CMD [ "./docker_entrypoint.sh" ]
