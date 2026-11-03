# moisture.py - example of a NON-car program: reads the soil moisture sensor
# Wiring: sensor AO (analog out) -> GPIO36, VCC -> 3.3V, GND -> GND
import time
from machine import ADC, Pin

DRY = 3200   # raw reading with the sensor in dry air  (calibrate this)
WET = 1300   # raw reading with the sensor in water     (calibrate this)

adc = ADC(Pin(36))
adc.atten(ADC.ATTN_11DB)
u = None
last = 0


def start(uart):
    global u
    u = uart
    u.send("Moisture monitor\n")


def step(cmds):
    global last
    if time.ticks_diff(time.ticks_ms(), last) >= 1000:
        last = time.ticks_ms()
        raw = adc.read()
        pct = max(0, min(100, (DRY - raw) * 100 // (DRY - WET)))
        u.send("Moisture: %d%% (raw %d)\n" % (pct, raw))


def stop():
    pass
