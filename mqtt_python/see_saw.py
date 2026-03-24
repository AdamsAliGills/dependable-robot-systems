from uservice import service
from spose import pose
from sedge import edge
from simu import imu
import time
import math

MIDDLE_DISTANCE = 0.3 # TODO check real value
BOTTOM_DISTANCE = 1.3 # TODO check real value

def get_tilt():
    return imu.gyroIntegral[1]

class SeeSaw():
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
                self.starting_tilt = get_tilt() # store the original tilt in degrees
                self.state = 1

            elif self.state == 1:
                current_tilt = get_tilt()
                print(f"tilt: {current_tilt}")
                if abs(current_tilt-self.starting_tilt) >= 1: #detect the ramp - reach the see-saw
                    pose.tripBreset()  #reset the distance record
                    edge.lineControl(0.1, followLeft=True) # slow down the speed
                    self.state = 2

            elif self.state == 2:
                '''Move to the middle and pick up the ball'''
                print(f"distance: {pose.tripB}")
                if pose.tripB > MIDDLE_DISTANCE:     # pose.tripB is the variable to record distance
                    edge.lineControl(0)
                    time.sleep(3) # TODO Control the servo to pick up the golf ball
                    #
                    #
                    # Pick up function
                    #
                    #
                    pose.tripBreset()
                    edge.lineControl(0.05, followLeft=True)
                    self.state = 3   
            
            elif self.state == 3:
                print(f"distance: {pose.tripB}")
               
                if pose.tripB > BOTTOM_DISTANCE: # When robot leave the see-saw
                    edge.lineControl(0)
                    self.state = 99

            else:
                print("% SeeSaw: complete")
                return True
            time.sleep(0.05)
        return False

