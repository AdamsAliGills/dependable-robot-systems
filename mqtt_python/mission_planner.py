from uservice import service
from round_about import roundAbout
from sedge import edge
import math
from detection_utils import (
    wait_ramp_bottom,
    wait_ramp_top,
    wait_turn,
    wait_end,
    wait_line,
)
import time
from scam import cam
from ball_in_hole import BallInHole
from balls_in_grid import BallsInGrid

LONG_RAMP_TILT = 8  # TODO check real value
SHORT_RAMP_TILT = 15  # TODO check real value


def sleep(t):
    start = time.time()
    while (time.time() - start < t) and not service.stop:
        time.sleep(0.01)


class missionPlanner:
    def __init__(self):
        self.planMission()
        # self.ballInHoleCaller()

    def planMission(self):
        edge.lineControl(0.2, True)

        # initialize servos
        service.send("robobot/cmd/T0", "servo 1 0 50")
        service.send("robobot/cmd/T0", "servo 2 0 50")
        sleep(0.3)
        service.send("robobot/cmd/T0", "servo 1 -400 50")
        service.send("robobot/cmd/T0", "servo 2 -200 50")

        print("DONE WITH BALL OP")
        wait_ramp_top(SHORT_RAMP_TILT, tolerance=3)
        print(f"START SECOND RAMP")
        edge.lineControl(0.25, followLeft=False)

        wait_ramp_bottom(SHORT_RAMP_TILT, tolerance=3)
        print(f"END SECOND RAMP")
        edge.lineControl(0.15, followLeft=False)

        sleep(2.5)
        edge.lineControl(0.0)

        service.send("robobot/cmd/ti", f"rc 0.3 0.0")
        sleep(5)
        service.send("robobot/cmd/ti", f"rc 0.0 -0.7")
        wait_turn(85)
        service.send("robobot/cmd/ti", f"rc 0.1 0.0")
        wait_end()
        service.send("robobot/cmd/ti", f"rc 0.0 -0.7")
        wait_turn(85)
        service.send("robobot/cmd/ti", f"rc 0.3 0.0")
        sleep(5.5)
        service.send("robobot/cmd/ti", f"rc 0.0 -0.7")
        wait_turn(85)
        service.send("robobot/cmd/ti", f"rc 0.1 0.0")
        edge.lineControl(0.15, followLeft=True)
        # knock over balls (im assuming u are knock them from straight position)
        # rotate over the balls
        radius = 0.33  # radius of the roundabout in meters
        speed = 0.2  # speed for the roundabout in meters/second
        t = 0  # traget angle
        angular_speed = math.copysign(speed / radius, t)
        service.send("robobot/cmd/ti", f"rc {speed} {angular_speed}")
        # ball detection
        # qr detection
        # ball detection
        # qr detection
        # back on line


if __name__ == "__main__":
    mp = missionPlanner()

