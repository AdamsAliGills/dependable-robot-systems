from uservice import service
from round_about import roundAbout


class missionPlanner():
    def __init__(self):
        try:
            self.planMission()
        except Exception as e:
            print(f"Error in mission planner: {e}")

    def planMission(self):
        print(f"Mission planner is planning the mission...")

    def roundAboutCaller(self):
        '''Caller for the roundabout mission'''
        r = roundAbout(135)
        r.execute()
    
    def seeSawCaller(self):
        '''Caller for the see saw mission'''
        pass

    def ballInHoleCaller(self):
        '''Caller for the ball in hole mission'''
        pass

