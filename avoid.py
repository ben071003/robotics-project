# avoid.py - drive forward, back up and turn away from obstacles
import time
import hw

u = None


def start(uart):
    global u
    u = uart
    hw.stop()
    u.send("Obstacle avoiding\n")


def step(cmds):
    if "S" in cmds.upper():      # S = emergency stop
        hw.stop()
        return
    if hw.distance_cm() < hw.OBSTACLE_CM:
        hw.stop()
        time.sleep_ms(100)
        hw.drive(-hw.DRIVE_SPEED, -hw.DRIVE_SPEED)   # back up a little
        time.sleep_ms(300)
        hw.drive(hw.TURN_SPEED, -hw.TURN_SPEED)      # spin right
        time.sleep_ms(400)
        hw.stop()
    else:
        hw.drive(hw.DRIVE_SPEED, hw.DRIVE_SPEED)


def stop():
    hw.stop()
