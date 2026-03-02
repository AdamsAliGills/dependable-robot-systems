#!/usr/bin/env python3

# /***************************************************************************
# *   Copyright (C) 2024 by DTU
# *   jcan@dtu.dk
# *
# *
# * The MIT License (MIT)  https://mit-license.org/
# *
# * Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# * and associated documentation files (the “Software”), to deal in the Software without restriction,
# * including without limitation the rights to use, copy, modify, merge, publish, distribute,
# * sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
# * is furnished to do so, subject to the following conditions:
# *
# * The above copyright notice and this permission notice shall be included in all copies
# * or substantial portions of the Software.
# *
# * THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# * INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# * PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# * FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# * ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# * THE SOFTWARE. */

from enum import Enum
import time as t
import numpy as np
import cv2 as cv
from datetime import *
from setproctitle import setproctitle

# robot function
from spose import pose
from sir import ir
from srobot import robot
from scam import cam
from sedge import edge
from sgpio import gpio
from scam import cam
from uservice import service

# Custom made mission functions
from mission_planner import missionPlanner


"""
for state machine logic
enums are implemented
all atributes are being assigned atm
"""


class State(Enum):
    INITIAL = 0
    FOLLOWLINE = 103


stateTime = datetime.now()


def stateTimePassed():
    return (datetime.now() - stateTime).total_seconds()


def driveToLine():
    """
    now it just has an ir threashold for anything less than 0.2
    0.2 is a distance that wont change with calibration script

    if ir < 0.2 we commad it to move forward
    but in practice it will spin in circles cuz contoler
    is not properly in sedge.py. lineCtrl variable
    implements unstable controller either from poor desgin choice
    or poor calibration

    if line lineValidCnt less than 4 then it will just move straight for abit
    """
    state = 0
    pose.tripBreset()
    dist_to_line = 0
    while not (service.stop):
        if state == 0:
            if ir.ir[0] < 0.2:
                service.send("robobot/cmd/ti", "rc 0.2 0.0")
                service.send("robobot/cmd/T0/", "lognow 3")
                service.send("robobot/cmd/T0", "servo 1 -800 300")
                state = 1
        elif state == 1:
            if pose.tripB > 1.0 or pose.tripBtimePassed() > 15:
                service.send(
                    "robobot/cmd/ti/", "rc 0.0 0.0"
                )  # (forward m/s, turn-rate rad/sec)
                state = 2
            if edge.lineValidCnt > 4:
                # start follow line
                edge.lineControl(0.2, True)
                service.send(
                    "robobot/cmd/T0", "servo 1 0 0"
                )  # (move servo to position 0 - front)
                dist_to_line = pose.tripB
                pose.tripBreset()
                print(" to state 10")
                state = 10
            pass
        elif state == 2:
            if abs(pose.velocity()) < 0.001:
                print(" to state 99")
                state = 99
        elif state == 10:
            if edge.lineValidCnt < 2:
                edge.lineControl(0, True)
                service.send(
                    "robobot/cmd/ti", "rc 0.0 0.0"
                )  # (forward m/s, turn-rate rad/sec)
                print(" to state 2")
                pose.tripBreset()
                state = 2
        else:
            print(
                f"# drive to line {dist_to_line:.3f}m, then along line {pose.tripB:.3f}m in {pose.tripBtimePassed():.3f} seconds"
            )
            service.send(
                "robobot/cmd/ti", "rc 0.0 0.0"
            )  # (forward m/s, turn-rate rad/sec)
            service.send("robobot/cmd/T0", "servo 1 500 200")  # (move servo down slow)
            break
        # print(f"# drive {state}, now {pose.tripB:.3f}m in {pose.tripBtimePassed():.3f} seconds, line valid cnt = {edge.lineValidCnt}")
        t.sleep(0.01)
    pass
    service.send("robobot/cmd/T0", "leds 16 0 0 0")  # end
    print("% Driving to line ------------------------- end")


def loop():
    """
    employs state machine style logic based on service command line arguments

    lineControl() initlizes some line control parameters for edge from the SEdge class form sedge.py
    but this function just has initlizations

    service.send() interfaces with teensy to implement commands

    103(line following)
    """
    from ulog import flog

    state = 0
    oldstate = -1
    service.send("robobot/cmd/T0", "leds 16 30 30 0")

    if service.args.edge:
        state = 103
    elif service.args.usestate > 0:
        state = service.args.usestate
    print(f"% Starting at state {state}")
    edge.lineControl(0, True)

    while not (service.stop):
        if state == 0:
            print("no args besides edge does anything")
            # edge line sensor values
            print(f"line sensor values:{edge.edge}")
            break
        elif state == 103:
            driveToLine()
            state = 100
        else:  # abort
            print(f"% Mission finished/aborted; state={state}")
            break

        if state != oldstate:
            flog.writeRemark(f"% State change from {oldstate} to {state}")
            print(f"% State change from {oldstate} to {state}")
            oldstate = state
            stateTime = datetime.now()
        t.sleep(0.1)
        pass  # end of while loop

    # end of mission, turn LEDs off and stop
    service.send("robobot/cmd/T0", "leds 16 0 0 0")
    gpio.set_value(20, 0)
    edge.lineControl(0, True)
    service.send("robobot/cmd/ti", "rc 0 0")
    service.send("robobot/cmd/T0", "servo 1 0 0")
    t.sleep(0.05)
    pass


def main():
    """
    starts mqtt client using the service object from the uservice.py file
    the service setup() can use optional command line arguments procesed by
    by bultin python argument parser object.

    setup() includes the setup() for all other objects connected to
    all the other scripts in the code
        gpio.setup()
        robot.setup()
        ir.setup()
        pose.setup()
        imu.setup()
        cam.setup()
        edge.setup()

    loop() is called on start
    """

    if service.process_running("mqtt-client"):
        print("% mqtt-client is already running - terminating")
        print("%   if it is partially crashed in the background, then try:")
        print("%     pkill mqtt-client")
        print("%   or, if that fails use the most brutal kill")
        print("%     pkill -9 mqtt-client")
    else:
        setproctitle("mqtt-client")
        print("% Starting")
        service.setup("localhost")
        if service.connected:
            loop()
        service.terminate()
    print("% Main Terminated")


if __name__ == "__main__":
    main()
