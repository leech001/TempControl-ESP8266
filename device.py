from machine import Pin
import uasyncio as asyncio


class Relay:
    def __init__(self, pin, delay=0, run=True, auto=True):    # Delay is pump run-out
        self.pin = pin
        self.delay = delay
        self.run = run
        self.auto = auto

    def on(self):
        self.run = True
        Pin(self.pin, Pin.OUT, value=0)
        return "Relay on pin %s is on" % self.pin

    async def off(self):
        self.run = False
        await asyncio.sleep(self.delay)
        Pin(self.pin, Pin.OUT, value=1)
        return "Relay on pin %s is off" % self.pin
