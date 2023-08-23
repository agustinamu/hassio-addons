#!/usr/bin/with-contenv bashio
# ==============================================================================
# Setup MQTT settings
# ==============================================================================
# shellcheck disable=SC1091

bashio::log.info "Preparing to start..."

bashio::config.require 'devices'
DEVICES=$(bashio::config 'devices')
DEVICE_JSON=$(jq --compact-output --null-input '$ARGS.positional' --args -- ${DEVICES[@]} | tr -d '\n' | tr -d '\'| sed -e 's/\"{/{/g' | sed -e 's/\}\"/}/g')
LOG_LEVEL=$(bashio::config 'log_level')


# Expose addon configuration through environment variables.
function export_config() {
    local key=${1}
    local subkey

    if bashio::config.is_empty "${key}"; then
        bashio::log.info "no mqtt config"
        return
    fi

    for subkey in $(bashio::jq "$(bashio::config "${key}")" 'keys[]'); do
        export "BLEE2MQTT_CONFIG_$(bashio::string.upper "${key}")_$(bashio::string.upper "${subkey}")=$(bashio::config "${key}.${subkey}")"
    done
}

export_config 'mqtt'
bashio::log.info "mqtt service"
host=$(bashio::services mqtt "host")
# bashio::log.info  "$(bashio::services 'mqtt' )"
bashio::log.info  ${host}


export BLEE2MQTT_CONFIG_MQTT_SERVER
export BLEE2MQTT_CONFIG_MQTT_SERVER_PORT
export BLEE2MQTT_CONFIG_MQTT_PASSWORD
export BLEE2MQTT_CONFIG_MQTT_USER

if bashio::config.is_empty 'mqtt' ; then
    bashio::log.info "mqtt empty"
    if bashio::var.true "$(bashio::services 'mqtt' 'ssl')"; then
        bashio::log.info "mqtt ssl"
        BLEE2MQTT_CONFIG_MQTT_SERVER="$(bashio::services 'mqtt' 'host')"
    else
        BLEE2MQTT_CONFIG_MQTT_SERVER="$(bashio::services 'mqtt' 'host')"
        bashio::log.info "mqtt no ssl"
    fi
    BLEE2MQTT_CONFIG_MQTT_SERVER_PORT="$(bashio::services 'mqtt' 'port')"
    BLEE2MQTT_CONFIG_MQTT_USER="$(bashio::services 'mqtt' 'username')"
    BLEE2MQTT_CONFIG_MQTT_PASSWORD="$(bashio::services 'mqtt' 'password')"
fi






# Crea el archivo JSON
cat << EOF > /usr/src/app/ble2mqtt.json
{
    "mqtt_host": "$BLEE2MQTT_CONFIG_MQTT_SERVER",
    "mqtt_port": $BLEE2MQTT_CONFIG_MQTT_SERVER_PORT,
    "mqtt_user": "$BLEE2MQTT_CONFIG_MQTT_USER",
    "mqtt_password": "$BLEE2MQTT_CONFIG_MQTT_PASSWORD",
    "log_level": "$LOG_LEVEL",
    "devices": ${DEVICE_JSON}
}
EOF

cat /usr/src/app/ble2mqtt.json
bluetoothd &
bashio::log.info "Starting Ble2MQTT..."
BLE2MQTT_CONFIG=/usr/src/app/ble2mqtt.json ble2mqtt
