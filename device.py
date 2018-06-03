from machine import Pin
import uasyncio as asyncio


class Relay:
    def __init__(self, pin, delay=0, auto=True):    # Delay is pump run-out
        self.pin = pin
        self.delay = delay
        self.auto = True

    def on(self):
        Pin(self.pin, Pin.OUT, value=0)
        return "Relay on pin %s is on" % self.pin

    async def off(self):
        await asyncio.sleep(self.delay)
        Pin(self.pin, Pin.OUT, value=1)
        return "Relay on pin %s is off" % self.pin
