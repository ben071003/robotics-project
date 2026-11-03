# hw.py - shared hardware helpers. Every program imports this.
#
# WIRING (L298N motor driver)
#   IN1 -> GPIO25   IN2 -> GPIO26   (left motor)
#   IN3 -> GPIO27   IN4 -> GPIO13   (right motor)
#   ENA -> GPIO32   ENB -> GPIO33   (speed, remove the jumpers on the L298N EN pins)
# ULTRASONIC (HC-SR04): VCC -> 5V, TRIG -> GPIO17,
#   ECHO -> GPIO16 THROUGH A VOLTAGE DIVIDER (1k + 2k) because Echo is 5V
# IR LINE SENSORS: left OUT -> GPIO34, right OUT -> GPIO35, VCC -> 3.3V
# All grounds (battery, L298N, ESP32, sensors) must be connected together.

import time
from machine import Pin, PWM, time_pulse_us

# ---- settings you can tune ----
DRIVE_SPEED = 70      # 0-100
TURN_SPEED = 60       # 0-100
OBSTACLE_CM = 20      # turn away when closer than this
BLACK = 1             # IR value over the black line (flip to 0 if reversed)

# ---- motors ----
in1, in2 = Pin(25, Pin.OUT), Pin(26, Pin.OUT)
in3, in4 = Pin(27, Pin.OUT), Pin(13, Pin.OUT)
ena = PWM(Pin(32), freq=1000)
enb = PWM(Pin(33), freq=1000)


def drive(left, right):
    """left/right: -100 (full back) to 100 (full forward)."""
    in1.value(1 if left > 0 else 0)
    in2.value(1 if left < 0 else 0)
    in3.value(1 if right > 0 else 0)
    in4.value(1 if right < 0 else 0)
    ena.duty_u16(min(abs(left), 100) * 655)
    enb.duty_u16(min(abs(right), 100) * 655)


def stop():
    drive(0, 0)


# ---- sensors ----
trig = Pin(17, Pin.OUT)
echo = Pin(16, Pin.IN)
ir_left = Pin(34, Pin.IN)
ir_right = Pin(35, Pin.IN)


def distance_cm():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    t = time_pulse_us(echo, 1, 30000)
    if t < 0:
        return 400
    return t * 0.0343 / 2
