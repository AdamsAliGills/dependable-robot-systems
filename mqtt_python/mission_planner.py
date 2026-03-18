from uservice import service
from round_about import roundAbout
from sedge import edge
from detection_utils import wait_ramp_bottom, wait_ramp_top, wait_turn, wait_end
import time

LONG_RAMP_TILT = 8 # TODO check real value
SHORT_RAMP_TILT = 15 # TODO check real value

def sleep(t):
    start = time.time()
    while (time.time() - start < t) and not service.stop:

        time.sleep(0.01)

class missionPlanner():
    def __init__(self):
        self.planMission()

    def planMission(self):
        edge.lineControl(0.3, followLeft=True)

        wait_turn(25)
        sleep(1)

        edge.lineControl(0.05, followLeft=True)

        r = roundAbout(-225)
        r.execute()

        edge.lineControl(0.3, followLeft=False)
        sleep(2)

        wait_ramp_bottom(LONG_RAMP_TILT, tolerance = 3)
        print(f"START FIRST RAMP")
        wait_ramp_top(LONG_RAMP_TILT, tolerance = 3)
        print(f"END FIRST RAMP")

        wait_ramp_top(SHORT_RAMP_TILT, tolerance = 3)
        print(f"START SECOND RAMP")
        wait_ramp_bottom(SHORT_RAMP_TILT, tolerance = 3)
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
        '''Caller for the roundabout mission'''
        tot_tests = 10
        n = roundAbout.test(tot_tests)
        print()
        print(f"===================== TESTS RESULTS =====================")
        print(f"{n} tests out of {tot_tests} were successful")
        print(f"=========================================================")
        print()

    
    def seeSawCaller(self):
        '''Caller for the see saw mission'''
        pass

    def ballInHoleCaller(self):
        '''Caller for the ball in hole mission'''
        pass

