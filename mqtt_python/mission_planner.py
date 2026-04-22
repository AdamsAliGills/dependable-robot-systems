from uservice import service
from round_about import roundAbout
from sedge import edge
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
        # edge.lineControl(0.2, followLeft=True)

        # wait_turn(25)
        # sleep(1)

        # edge.lineControl(0.05, followLeft=True)

        # r = roundAbout(-225)
        # r.execute()

        edge.lineControl(0.2, followLeft=False)

        balls_in_grid = BallsInGrid()
        balls_in_grid.off_line_check()
        balls_in_grid.additional_time()

        # wait_turn(80)
        print(f"TURN DETECTED")

        sleep(1.5)
        edge.lineControl(0)
        service.send("robobot/cmd/ti", f"rc 0.2 0.0")
        sleep(1)

        edge.lineControl(0.2, followLeft=True)

        sleep(3.5)

        edge.lineControl(0.05, followLeft=True)

        r = roundAbout(-225)
        r.execute()

        edge.lineControl(0.2, followLeft=True)
        wait_end()


if __name__ == "__main__":
    mp = missionPlanner()
