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


if __name__ == "__main__":
    mp = missionPlanner()
