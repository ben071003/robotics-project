# manual.py - drive with F B L R S from the phone
import hw

u = None


def start(uart):
    global u
    u = uart
    hw.stop()
    u.send("Manual mode\n")


def step(cmds):
    for c in cmds.upper():
        if c == "F":
            hw.drive(hw.DRIVE_SPEED, hw.DRIVE_SPEED)
        elif c == "B":
            hw.drive(-hw.DRIVE_SPEED, -hw.DRIVE_SPEED)
        elif c == "L":
            hw.drive(-hw.TURN_SPEED, hw.TURN_SPEED)
        elif c == "R":
            hw.drive(hw.TURN_SPEED, -hw.TURN_SPEED)
        elif c == "S":
            hw.stop()
    if not u.conns:
        hw.stop()   # safety: stop if the phone disconnects


def stop():
    hw.stop()
