import gc
import onewire, ds18x20
import config
import uasyncio as asyncio
import wifi
import machine
import utime as time
import usocket as socket
import ustruct as struct
from umqtt.simple import MQTTClient


gc.enable()
wifi.activate()
int_err_count = 0
ping_mqtt = 0
ping_fail = 0

dat = machine.Pin(config.temp_pin)
ds = ds18x20.DS18X20(onewire.OneWire(dat))
roms = ds.scan()

while len(roms) < 1:
    print("Temp sensor not found")
    time.sleep(10)
    roms = ds.scan()
print("Found DS18B20 devices:", roms)

use_topic = config.CONFIG['DEVICE_TYPE'] + "/" + config.CONFIG['DEVICE_PLACE'] + "/" + config.CONFIG[
    'DEVICE_PLACE_NAME'] + "/"
device_topic = config.CONFIG['DEVICE_TYPE'] + "/" + config.CONFIG['DEVICE_PLACE'] + "/" + config.CONFIG[
    'DEVICE_PLACE_NAME'] + "/" + config.CONFIG['DEVICE_ID'] + "/"


def time_now():
    ntp_query = bytearray(48)
    ntp_query[0] = 0x1b
    try:
        addr = socket.getaddrinfo(config.host, 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.sendto(ntp_query, addr)
        msg = s.recv(48)
        s.close()
        val = struct.unpack("!I", msg[40:44])[0]
        return val - config.ntp_delta
    except Exception as e:
        print("Error: [Exception] %s: %s" % (type(e).__name__, e))
        time.sleep(60)
        machine.reset()


def settime():
    try:
        t = time_now()
        tm = time.localtime(t)
        tm = tm[0:3] + (0,) + tm[3:6] + (0,)
        machine.RTC().datetime(tm)
    except Exception as e:
        print("Error: [Exception] %s: %s" % (type(e).__name__, e))
        time.sleep(60)
        machine.reset()


settime()


# Check Internet connection
def internet_connected(host='8.8.8.8', port=53):
    global int_err_count
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        try:
            s.connect((host, port))
            int_err_count = 0
            return True
        except Exception as e:
            print("Error Internet connect: [Exception] %s: %s" % (type(e).__name__, e))
            return False
        finally:
            s.close()


# Check sensor
async def check_sensor():
    while True:
        print("Check sensor ...")
        ds.convert_temp()
        await asyncio.sleep(0.75)
        for item in roms:
            device_id = ""
            for b_id in item:
                device_id += str(b_id)
            client.publish(device_topic + "data/temp/%s" % device_id, "%s" % ds.read_temp(item))
            if device_id == config.CONFIG['TEMP_SENSOR_ID']:
                temp_control(ds.read_temp(item))
        await asyncio.sleep(1)


def temp_control(sensor_temp):
    if sensor_temp <= (config.CONFIG['TEMP'] - config.CONFIG['TEMP_HYSTERESIS']):
        print("Heat ON")
        for relay in config.relays:
            if relay.auto is True:
                relay.on()
    elif sensor_temp >= (config.CONFIG['TEMP'] + config.CONFIG['TEMP_HYSTERESIS']):
        print("Heat OFF")
        for relay in config.relays:
            if relay.auto is True:
                if relay.run is True:
                    loop.create_task(relay.off())
    else:
        print("Temp OK")


def on_message(topic, msg):
    global ping_fail
    print("Topic: %s, Message: %s" % (topic, msg))

    if "/check/mqtt" in topic:
        if int(msg) == ping_mqtt:
            print("MQTT pong true...")
            ping_fail = 0
        else:
            print("MQTT pong false... (%i)" % ping_fail)

    if "/check/ping" in topic:
        send_mqtt_pong(msg)

    if "/relay" in topic:
        s_topic = str(topic).split("/")
        id_relays = int(s_topic[6][0])
        print(id_relays)
        if msg == b"on":
            config.relays[id_relays].on()
            config.relays[id_relays].auto = False
        if msg == b"off":
            if config.relays[id_relays].run is True:
                loop.create_task(config.relays[id_relays].off())
            config.relays[id_relays].auto = False
        if msg == b"auto_on":
            config.relays[id_relays].auto = True
        if msg == b"auto_off":
            config.relays[id_relays].auto = False


# Pong MQTT connect
def send_mqtt_pong(pong_msg):
    print(pong_msg.decode("utf-8"))
    client.publish(device_topic + "/state/check/pong/",
                   pong_msg.decode("utf-8"))


# Check MQTT brocker
async def check_mqtt():
    global ping_fail
    global ping_mqtt
    while True:
        await asyncio.sleep(10)
        ping_mqtt = time.time()
        client.publish(device_topic + "state/check/mqtt/", "%s" % ping_mqtt)
        print("Send MQTT ping (%i)" % ping_mqtt)
        ping_fail += 1

        if ping_fail >= config.CONFIG['MQTT_CRIT_ERR']:
            print("MQTT ping false... reset (%i)" % ping_fail)
            machine.reset()

        if ping_fail >= config.CONFIG['MQTT_MAX_ERR']:
            print("MQTT ping false... reconnect (%i)" % ping_fail)
            client.disconnect()
            mqtt_reconnect()


# MQTT reconnect
def mqtt_reconnect():
    global client
    try:
        client = MQTTClient(config.CONFIG['MQTT_CLIENT_ID'], config.CONFIG['MQTT_BROKER'],
                            user=config.CONFIG['MQTT_USER'],
                            password=config.CONFIG['MQTT_PASSWORD'], port=config.CONFIG['MQTT_PORT'])
        client.DEBUG = True
        client.set_callback(on_message)
        client.connect(clean_session=True)
        if config.CONFIG['DEVICE_ID'] == config.CONFIG['DEVICE_ID_USE']:
            client.subscribe(use_topic + "#")
            print("ESP8266 is Connected to %s and subscribed to %s topic" % (
                config.CONFIG['MQTT_BROKER'], use_topic + "#"))
        else:
            client.subscribe(device_topic + "#")
            print("ESP8266 is Connected to %s and subscribed to %s topic" % (
                config.CONFIG['MQTT_BROKER'], device_topic + "#"))

        client.publish(device_topic + "info/", "%s" % [config.CONFIG['DEVICE_TYPE'], config.CONFIG['DEVICE_PLACE'],
                                                       config.CONFIG['DEVICE_PLACE_NAME'], config.CONFIG['DEVICE_ID']])
    except Exception as e:
        print("Error in MQTT reconnection: [Exception] %s: %s" % (type(e).__name__, e))


# Check MQTT message
async def check_message():
    while True:
        await asyncio.sleep(1)
        print("Check message...")
        try:
            client.check_msg()
        except Exception as e:
            print("Error in mqtt check message: [Exception] %s: %s" % (type(e).__name__, e))


# Check Internet connected and reconnect
async def check_internet():
    global int_err_count
    try:
        while True:
            await asyncio.sleep(60)
            print("Check Internet connect... ")
            if not internet_connected():
                print("Internet connect fail...")
                int_err_count += 1

                if int_err_count >= config.CONFIG['INT_CRIT_ERR']:
                    client.disconnect()
                    wifi.wlan.disconnect()
                    machine.reset()

                if int_err_count >= config.CONFIG['INT_MAX_ERR']:
                    print("Internet reconnect")
                    client.disconnect()
                    wifi.wlan.disconnect()
                    wifi.activate()
    except Exception as e:
        print("Error in Internet connection: [Exception] %s: %s" % (type(e).__name__, e))


mqtt_reconnect()
try:
    loop = asyncio.get_event_loop()
    loop.create_task(check_sensor())
    loop.create_task(check_message())
    loop.create_task(check_internet())
    loop.create_task(check_mqtt())
    loop.run_forever()
except Exception as e:
    print("Error: [Exception] %s: %s" % (type(e).__name__, e))
    time.sleep(60)
    machine.reset()
