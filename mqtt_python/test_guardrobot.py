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

from guard_robot import GuardRobot

test = GuardRobot()

'''Check the value of ENTRANCE_DISTANCE'''
def Distence_test():
    while not service.stop:
        dis = ir.ir[1]
        print(f"Distance between Oscar and Guard robot: {dis} \n")
        t.sleep(0.1)

'''Check the value of MISSION_DISTANCE'''
def Mission_Lenght_test():
    pose.tripBreset()
    dis = pose.tripB
    while not service.stop:
        print(f"Distance: {dis} \n")
        t.sleep(0.1)


if __name__ == "__main__":
    task = int(input("Choose task: "))
    if task == 1:
        Distence_test()
    if task == 2:
        Mission_Lenght_test()
    if task == 3:
        test = GuardRobot()
        test.execute()