# line.py - follow a black line with two IR sensors
import hw

u = None


def start(uart):
    global u
    u = uart
    hw.stop()
    u.send("Line following\n")


def step(cmds):
    if "S" in cmds.upper():      # S = emergency stop
        hw.stop()
        return
    l = hw.ir_left.value() == hw.BLACK
    r = hw.ir_right.value() == hw.BLACK
    if not l and not r:          # line between the sensors -> straight
        hw.drive(hw.DRIVE_SPEED, hw.DRIVE_SPEED)
    elif l and not r:            # line drifted left -> steer left
        hw.drive(-hw.TURN_SPEED // 2, hw.TURN_SPEED)
    elif r and not l:            # line drifted right -> steer right
        hw.drive(hw.TURN_SPEED, -hw.TURN_SPEED // 2)
    else:                        # both on black (junction / end) -> stop
        hw.stop()


def stop():
    hw.stop()
