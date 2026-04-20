from uservice import service
from round_about import roundAbout
from sedge import edge
from detection_utils import wait_ramp_bottom, wait_ramp_top, wait_turn, wait_end
import time
from scam import cam
from ball_in_hole import BallInHole

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
        sleep(3)

        print("#############################################")
        wait_ramp_bottom(LONG_RAMP_TILT, tolerance=3)
        print("#############################################")
        print(f"START FIRST RAMP")

        sleep(1)
        edge.lineControl(
            0.3, followLeft=False
        )  # DO NOT CHANGE THIS VALUE, IT WILL MESS WITH THE ballInHole timing

        print("#############################################")
        wait_ramp_top(LONG_RAMP_TILT, tolerance=2)
        print("#############################################")
        print(f"END FIRST RAMP")

        # Deal with camera
        edge.lineControl(0.0, followLeft=False)
        service.send("robobot/cmd/ti", f"rc 0 0.0")

        print("#############################################")
        print("STARTING BALL IN HOLE OP")
        print("#############################################")

        self.ballInHoleCaller()
        edge.lineControl(0.2, True)

        print("#############################################")
        print("DONE WITH BALL OP")
        print("#############################################")
        wait_ramp_top(SHORT_RAMP_TILT, tolerance=3)
        print(f"START SECOND RAMP")
        edge.lineControl(0.25, followLeft=False)

        wait_ramp_bottom(SHORT_RAMP_TILT, tolerance=3)
        print(f"END SECOND RAMP")
        edge.lineControl(0.15, followLeft=True)

        wait_turn(80)
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

    def roundAboutCaller(self):
        """Caller for the roundabout mission"""
        tot_tests = 10
        n = roundAbout.test(tot_tests)
        print()
        print(f"===================== TESTS RESULTS =====================")
        print(f"{n} tests out of {tot_tests} were successful")
        print(f"=========================================================")
        print()

    def seeSawCaller(self):
        """Caller for the see saw mission"""
        pass

    def ballInHoleCaller(self):
        """Caller for the ball in hole mission"""

        edge.lineControl(0)  # stop for detecting ball

        BallInHole()


if __name__ == "__main__":
    mp = missionPlanner()
