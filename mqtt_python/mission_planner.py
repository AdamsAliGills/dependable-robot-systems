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
        edge.lineControl(0.2, False)
        sleep(2.2)
        ball_o = BallInHole("orange")
        ball_o.knock_down_cup()
        # rotate over the balls
        # qr detection
        # ball detection
        # qr detection
        # back on line


if __name__ == "__main__":
    mp = missionPlanner()

