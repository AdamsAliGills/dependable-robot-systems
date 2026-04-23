from uservice import service
from spose import pose
from sedge import edge
from simu import imu
from datetime import *
import time
import math
from ball_in_hole import BallInHole

def get_yaw():
    return imu.gyroIntegral[2]


stateTime = datetime.now()

def stateTimePassed():
  return (datetime.now() - stateTime).total_seconds()

pickup = BallInHole()

class SeeSaw():

    
    MIDDLE_DISTANCE = 0.85 # TODO check real value
    BOTTOM_DISTANCE = 1.0 # TODO check real value


    def __init__(self):
        '''Constructor for the SeeSaw mission'''
        self.name = "SeeSaw"
        self.state = 0
        print("-----------------------------------------")
        print("     INITIALIZING SEESAW MISSION     ")
        print("-----------------------------------------")

    def execute(self):
        '''Call this while following the line'''
        print("% SeeSaw: starting")
        while not service.stop:
            if self.state == 0:
                self.starting_yaw = get_yaw() # store the original yaw in degrees
                self.state = 1

            elif self.state == 1:
                current_yaw = get_yaw()
                print(f"yaw: {current_yaw}")
                if abs(current_yaw-self.starting_yaw) >= 75: #detect the turning -- reach the see-saw
                    pose.tripBreset()  #reset the distance record
                    edge.lineControl(0.15, followLeft=True) # slow down the speed
                    self.state = 2

            elif self.state == 2:
                '''Move to the middle and pick up the ball'''
                print(f"distance: {pose.tripB}")
                if pose.tripB > self.MIDDLE_DISTANCE:     # pose.tripB is the variable to record distance
                    edge.lineControl(0)
                    service.send("robobot/cmd/ti","rc 0.0 0.0")
                    self.state = 3  

            elif self.state == 3:
                reached = pickup._approaching()
                if reached:
                    service.send("robobot/cmd/ti", "rc 0 0")
                    if self.final_alignment == False:
                        print("#####################")
                        print("CHECKING FINAL ALLIGNMENT")
                        print("#####################")
                        self.state = self.ALIGNING
                        self.final_alignment = True
                    self.state = 4
                    print(f"[BallInHole] Ball in reach, transitioning to PICKING_UP")

            elif self.state == 4:
                pickup._picking_up()
                print(f"[BallInHole] Ball picked up, transitioning to NAVIGATING_HOLE")
                self.state = 5

            elif self.state == 5:
                pose.tripBreset()
                edge.lineControl(0.04, followLeft=True)
                self.state = 11 

            elif self.state == 11:
                if pose.tripBtimePassed() > 7:
                    pose.tripBreset()
                    edge.lineControl(0.10, followLeft=True)
                    self.state = 12 
            
            
            elif self.state == 12:
                print(f"distance: {pose.tripB}")
               
                if pose.tripB > self.BOTTOM_DISTANCE: # When robot leave the see-saw
                    edge.lineControl(0)
                    self.state = 99

            else:
                print("% SeeSaw: complete")
                return True
            time.sleep(0.05)
        return False

