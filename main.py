# main.py - LAUNCHER. Runs one program from /programs at a time and lets the phone
# list programs and switch between them without reconnecting.
#
# Phone -> ESP32 messages:
#   single letters (F B L R S A T M ...)  -> passed to the running program
#   #LIST\n          -> ESP32 replies  #PROGS:name1,name2,...  and  #ACTIVE:name
#   #RUN:name\n      -> stop current program, start /programs/name.py
#
# To add a new project: copy a file into /programs with these 3 functions:
#   start(uart)  - called once when the program is selected
#   step(cmds)   - called every ~20 ms; cmds = letters received from the phone
#   stop()       - called when switching away (turn things off here)

import sys
import os
import time
import hw
from ble_uart import BLEUart

sys.path.append("/programs")

uart = BLEUart("ESP32-CAR")
prog = None
active = ""
pending = ""


def list_programs():
    names = []
    for f in os.listdir("/programs"):
        if f.endswith(".py") and not f.startswith("_"):
            names.append(f[:-3])
    names.sort()
    return names


def switch(name):
    global prog, active
    if name not in list_programs():
        uart.send("#ERR:no program " + name + "\n")
        return
    if prog:
        try:
            prog.stop()
        except Exception:
            pass
    hw.stop()
    sys.modules.pop(name, None)   # reload so edited files take effect
    try:
        prog = __import__(name)
        prog.start(uart)
        active = name
        uart.send("#ACTIVE:" + name + "\n")
    except Exception as e:
        prog = None
        active = ""
        hw.stop()
        uart.send("#ERR:" + str(e) + "\n")


def handle(line):
    line = line.strip()
    if line == "LIST":
        uart.send("#PROGS:" + ",".join(list_programs()) + "\n")
        uart.send("#ACTIVE:" + active + "\n")
    elif line.startswith("RUN:"):
        switch(line[4:])


def parse(data):
    """Split incoming bytes into protocol lines (#...) and plain command letters."""
    global pending
    cmds = ""
    for b in data:
        ch = chr(b)
        if pending:
            if ch == "\n":
                handle(pending[1:])
                pending = ""
            elif len(pending) > 40:
                pending = ""
            else:
                pending += ch
        elif ch == "#":
            pending = "#"
        else:
            cmds += ch
    return cmds


hw.stop()
switch("manual")
print("Launcher ready. Programs:", list_programs())

while True:
    cmds = parse(uart.read())
    if prog:
        try:
            prog.step(cmds)
        except Exception as e:
            hw.stop()
            uart.send("#ERR:" + str(e) + "\n")
            prog = None
            active = ""
    time.sleep_ms(20)
