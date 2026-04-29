from uservice import service
from stair_climb import StairClimb
from sedge import edge

class missionPlanner():
    def __init__(self):
        self.planMission()

    def planMission(self):
        print(f"Mission planner is planning the mission...")
        self.stairClimbCaller()

    def stairClimbCaller(self):
        '''Caller for the stair climb mission'''
        tot = 10
        succ = StairClimb.test(tot)
        print(f"{succ}/{tot} tests successful")
