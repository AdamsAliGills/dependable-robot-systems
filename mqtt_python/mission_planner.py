from uservice import service
from stair_climb import stairClimb
from sedge import edge

class missionPlanner():
    def __init__(self):
        self.planMission()

    def planMission(self):
        print(f"Mission planner is planning the mission...")
        self.stairClimbCaller()

    def stairClimbCaller(self):
        '''Caller for the stair climb mission'''
        s = stairClimb()
        s.execute()
