from uservice import service
from round_about import roundAbout
from sedge import edge
from detection_utils import wait_ramp_bottom, wait_ramp_top

LONG_RAMP_TILT = 8 # TODO check real value
SHORT_RAMP_TILT = 15 # TODO check real value

class missionPlanner():
    def __init__(self):
        try:
            self.planMission()
        except Exception as e:
            print(f"Error in mission planner: {e}")

    def planMission(self):
        print(f"Mission planner is planning the mission...")

        edge.lineControl(0.2, followLeft=True)

        r = roundAbout(-225)
        r.execute()

        edge.lineControl(0.2, followLeft=False)

        wait_ramp_bottom(LONG_RAMP_TILT)
        wait_ramp_top(LONG_RAMP_TILT)

        wait_ramp_top(SHORT_RAMP_TILT)
        wait_ramp_bottom(SHORT_RAMP_TILT)
        return

        # TODO detect 90 degrees and then go straight (?)

        edge.lineControl(0.2, followLeft=True)

        r = roundAbout(-225)
        r.execute()




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

