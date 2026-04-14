import time as t
#import select
import numpy as np
import cv2 as cv
from datetime import *
from setproctitle import setproctitle
# robot function
from spose import pose
from sir import ir
from srobot import robot
from scam import cam
from sedge import edge
from sgpio import gpio
from scam import cam
from uservice import service

class GuardRobot: 
    
    ENTRANCE_DISTANCE = 0.3  #when  TODO check the real value 
    MIN_DISTANCE = 0.2
    MISSION_DISTANCE = 1.6 #TODO check the real value

    def __init__(self):
        self.state = 0
        

    def execute(self):
        while not service.stop:

            if self.state == 0:
                pose.tripBreset() 

                if ir.ir[1] < self.ENTRANCE_DISTANCE: #ir[1] is the distance sensor. 
                    #When guard robot close to Oscar
                    t.sleep(1.5) #Wait for guard robot to pass
                    service.send("robobot/cmd/ti","rc 0.2 0.0")
                    self.state = 1
                
            elif self.state == 1:
                if edge.lineValidCnt > 4: #Detect the line
                    edge.lineControl(0.15, False)
                    self.state = 2

            elif self.state == 2:
                if ir.ir[1] < self.MIN_DISTANCE: # Oscar is too close to the guard robot
                    edge.lineControl(0)
                    service.send("robobot/cmd/ti","rc 0.0 0.0")
                    t.sleep(2)  #Wait 2 seconds, then move again
                    edge.lineControl(0.15, False)
                    #service.send("robobot/cmd/ti","rc 0.2 0.0")

                
                if pose.tripB > self.MISSION_DISTANCE: #Mission is finished
                    edge.lineControl(0)
                    pose.tripBreset()
                    service.send("robobot/cmd/ti","rc 0.2 0.0")
                    self.state = 3

            elif self.state == 3:
                if pose.tripB > 0.2:
                    service.send("robobot/cmd/ti","rc 0.0 0.0")
                    self.state = 99

            else:
                print("GuardRobot: complete")
                return True
            
            t.sleep(0.05)

        return False
    
                
                