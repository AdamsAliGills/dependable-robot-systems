from uservice import service


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
        pass
    
    def seeSawCaller(self):
        '''Caller for the see saw mission'''
        pass

    def ballInHoleCaller(self):
        '''Caller for the ball in hole mission'''
        pass

