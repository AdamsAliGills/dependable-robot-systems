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
        r = roundAbout(135)

        edge.lineControl(0.2)
        r.execute()
        edge.lineControl(0.2)
    
    def seeSawCaller(self):
        '''Caller for the see saw mission'''
        pass

    def ballInHoleCaller(self):
        '''Caller for the ball in hole mission'''
        pass

