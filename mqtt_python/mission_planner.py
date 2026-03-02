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
        self.roundAboutCaller()

    def roundAboutCaller(self):
        '''Caller for the roundabout mission'''
        return roundAbout()

