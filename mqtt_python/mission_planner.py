from uservice import service
from round_about import roundAbout
from sedge import edge

class missionPlanner():
    def __init__(self):
        try:
            self.planMission()
        except Exception as e:
            print(f"Error in mission planner: {e}")

    def planMission(self):
        print(f"Mission planner is planning the mission...")
        self.roundAboutCaller()

    def roundAboutCaller(self):
        '''Caller for the roundabout mission'''
        tot_tests = 10
        n = roundAbout.test(tot_tests)
        print()
        print(f"===================== TESTS RESULTS ============================")
        print(f"{n} tests out of {tot_tests} were successful")
        print(f"---------TESTS RESULTS-------------")
        print()

    
    def seeSawCaller(self):
        '''Caller for the see saw mission'''
        pass

    def ballInHoleCaller(self):
        '''Caller for the ball in hole mission'''
        pass

