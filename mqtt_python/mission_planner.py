from uservice import service
from round_about import roundAbout
from ball_in_hole import ballInHole
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
        return roundAbout()
    
    def seeSawCaller(self):
        pass

    def ballInHoleCaller(self):
        '''Caller for the ball in hole mission'''
        return ballInHole()

