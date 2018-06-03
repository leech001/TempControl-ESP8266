import device
ntp_delta = 3155673600
host = "pool.ntp.org"

temp_pin = 12
relays = (device.Relay(5, 0), device.Relay(4, 3), device.Relay(0, 4), device.Relay(2, 5))

# Modify below section as required
CONFIG = {
    "MQTT_BROKER": "example.com",
    "MQTT_USER": "user",
    "MQTT_PASSWORD": "pass",
    "MQTT_PORT": 1883,
    "MQTT_CLIENT_ID": "ESP_TEMP_01",
    "MQTT_MAX_ERR": 5,
    "MQTT_CRIT_ERR": 10,
    "DEVICE_TYPE": "temp",
    "DEVICE_PLACE": "dacha",
    "DEVICE_PLACE_NAME": "kitchen",
    "DEVICE_ID": "01",
    "DEVICE_ID_USE": "01",
    "WIFI_AP": "AP_NAME",
    "WIFI_PASSWORD": "PASS",
    "INT_MAX_ERR": 20,
    "INT_CRIT_ERR": 50,
    "TEMP_HYSTERESIS": 0.5,
    "TEMP": 29.0,
    "TEMP_SENSOR_ID": "40255250105161225116",
    "HEATER": True,
    "TIME_NOTIFY": 180
}
