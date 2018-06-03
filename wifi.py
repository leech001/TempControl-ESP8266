import network
import config
global wlan

def activate():
    global wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(config.CONFIG['WIFI_LOGIN'], config.CONFIG['WIFI_PASSWORD'])
        while not wlan.isconnected():
            pass
        print('Network config:', wlan.ifconfig())
