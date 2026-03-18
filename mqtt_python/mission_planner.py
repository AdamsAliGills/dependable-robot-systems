from uservice import service
from round_about import roundAbout
from ball_in_hole import BallInHole


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

    def ballInHoleCaller(self,image):
        '''Caller for the ball in hole mission'''
        print("---------------------------")
        print("Executing image analysis...")
        print("---------------------------")
        BallInHole()
        

