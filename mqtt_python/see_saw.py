from uservice import service
from spose import pose
from sedge import edge
from simu import imu
from datetime import *
import time
import math
from ball_in_hole import BallInHole

#Pick up orange golf ball
pickup = BallInHole("orange")

stateTime = datetime.now()

def stateTimePassed():
  return (datetime.now() - stateTime).total_seconds()

def get_yaw():
    return imu.gyroIntegral[2]


class SeeSaw():

    MIDDLE_DISTANCE = 0.75 # TODO check real value
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
                service.send("robobot/cmd/T0", "servo 1 -350 100") #raise the arm
                service.send("robobot/cmd/T0", "servo 2 -200 150") # open the gripper
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
                reached = pickup._approaching() # approach to the golf ball
                if reached:
                    service.send("robobot/cmd/ti", "rc 0 0")
                    self.state = 4
                    print(f"[BallInHole] Ball in reach, transitioning to PICKING_UP")

            elif self.state == 4:
                pickup._picking_up() # pick up the golf ball
                # Keep the arm down for robot balance
                print(f"[BallInHole] Ball picked up, transitioning to NAVIGATING_HOLE")
                #service.send("robobot/cmd/T0", "servo 1 657 100")  # Lower gripper down
                self.state = 5

            elif self.state == 5:
                pose.tripBreset()
                edge.lineControl(0.04, followLeft=True) # slowly move down the see saw
                self.state = 11 

            elif self.state == 11:
                
                if pose.tripBtimePassed() > 7:
                    #service.send("robobot/cmd/T0", "servo 1 -400 100")
                    pose.tripBreset()
                    edge.lineControl(0.15, followLeft=True)
                    # accelerate from 0.04m/s to 0.15m/s for saving time 
                    service.send("robobot/cmd/T0", "servo 1 600 100")
                    #Slightly raise arm
                    self.state = 12 

            elif self.state == 12:
                if pose.tripB > 0.3:
                    service.send("robobot/cmd/T0", "servo 1 -400 100") #raise the arm
                    edge.lineControl(0)
                    service.send("robobot/cmd/ti", "rc 0.15 0.0")
                    self.state = 13
                    

            elif self.state == 13:
                print(f"distance: {pose.tripB}")
                if pose.tripB > self.BOTTOM_DISTANCE: # When robot leave the see-saw
                    #service.send("robobot/cmd/T0", "servo 1 -400 100") #raise the arm
                    service.send("robobot/cmd/ti", "rc 0.0 0.0")
                    
                    self.state = 99

            else:
                print("% SeeSaw: complete")
                return True
            time.sleep(0.05)
        return False

