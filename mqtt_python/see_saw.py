from uservice import service
from spose import pose
from sedge import edge
from simu import imu
from datetime import *
import time
import math
import cv2
#from ball_in_hole_2 import BallInHole_2
from scam_calibration import CameraCalib
from scam import cam
from detection_utils import wait_turn
from ball_tracking import ball_tracking
from hole_detection import hole_tacking

class PickUp:

    def __init__(self,ball_color):
        self.state = 0
        self.in_center = False
        self.final_alignment = False
        self.calib = CameraCalib()
        pose.tripBreset()
        self.start_heading = 0
        self.ball_color = ball_color

    def _wait_for_camera(self, timeout=10.0):
        """Block until camera produces a valid frame or timeout."""
        print("[BallInHole] Waiting for camera...")
        start = time.time()
        while time.time() - start < timeout:
            ok, img, _ = cam.getImage()
            if ok and img is not None:
                print("[BallInHole] Camera ready.")
                return
            time.sleep(0.2)
        print(
            "[BallInHole] WARNING: Camera not ready after timeout, proceeding anyway."
        )    

    def _searching_golf_ball(self,img,ball_color):
        '''Searching for ball with parameter for different balls'''
        center, radius = ball_tracking(img,display = False,ball_color=ball_color)
        return center,radius

    def _aligning(
        self, center
    ):  # TODO: Need to adjust this such that it doesn't get stuck on minor adjustments
        """Steer robot such the ball center is centered in frame for x-axis"""
        TARGET_X = 288
        TURN_RATE = 0.5
        TOLERANCE = 0.025
        KP = 0.5  # tune this
        MIN_TURN = 0.2  # minimum to overcome friction
        MAX_TURN = 0.6  # safety clamp
        TOLERANCE = 0.017  # radians

        angle_x, _ = self.calib.pixel_to_angle(center[0], center[1])
        target_angle_x, _ = self.calib.pixel_to_angle(TARGET_X, center[1])
        error = angle_x - target_angle_x

        print(f"[Align] error={error:.4f}")

        # Stop condition
        if abs(error) < TOLERANCE:
            service.send("robobot/cmd/ti", "rc 0 0")
            return True

        # Proportional control
        turn = -KP * error

        # Deadband compensation (THIS FIXES YOUR ISSUE)
        if abs(turn) < MIN_TURN:
            turn = MIN_TURN * (1 if turn > 0 else -1)

        # Clamp
        turn = max(min(turn, MAX_TURN), -MAX_TURN)

        service.send("robobot/cmd/ti", f"rc 0 {turn}")

        return False
    
    def _approaching(self, at_end=False):
        """Driving towards ball, maybe parallel thread with camera input?"""
        TARGET_Y = 357
        TOLERANCE_Y = 20  # pixels, tune this

        img = self.get_img()
        if img is None:
            return False
        
        center, radius = self._searching_golf_ball(img,self.ball_color)
        if center is None:
            return False

        error_y = (
            TARGET_Y - center[1]
        )  # positive = ball too far (low y), need to drive forward
        print(f"[Approaching] ball y={center[1]}, target y={TARGET_Y}, error={error_y}")

        if abs(error_y) < TOLERANCE_Y:
            return True  # reached pickup position

        service.send("robobot/cmd/ti", "rc 0.07 0")
        return False
    
    def get_img(self):
        """get image from rasp camera and return it also undistorted via calibration"""
        if cam.useCam:
            ok, img, imgTime = cam.getImage()
            if not ok:  # size(img) == 0):
                if cam.imageFailCnt < 5:
                    print("% Failed to get image.")
        return img

    def _picking_up(self):
        """Pick up golf ball with servo arms and CV"""

        time.sleep(0.5)
        service.send("robobot/cmd/T0", "servo 1 640 100")  # Lower gripper down
        time.sleep(2)
        service.send(
            "robobot/cmd/T0", "servo 2 590 150"
        )  # close gripper ### to open its -200
        time.sleep(2)

#Pick up orange golf ball
pickup = PickUp("orange")

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
                service.send("robobot/cmd/T0", "servo 2 0 150") # open the gripper
                self.state = 1

            elif self.state == 1:
                current_yaw = get_yaw()
                print(f"yaw: {current_yaw}")
                wait_turn(60)
                #if abs(current_yaw-self.starting_yaw) <= -10: #detect the turning -- reach the see-saw
                pose.tripBreset()  #reset the distance record
                edge.lineControl(0.08, followLeft=False) # slow down the speed
                self.state = 20

            elif self.state == 20:
                if pose.tripBtimePassed() > 5:
                    edge.lineControl(0.15, followLeft=False) 
                    self.state = 2

            elif self.state == 2:
                '''Move to the middle and pick up the ball'''
                print(f"distance: {pose.tripB}")
                if pose.tripB > self.MIDDLE_DISTANCE:     # pose.tripB is the variable to record distance
                    edge.lineControl(0)
                    service.send("robobot/cmd/ti","rc 0.0 0.0")
                    self.state = 3  

            elif self.state == 3:
                img = pickup.get_img()
                center, radius = pickup._searching_golf_ball(img,"orange")
                self.ball_center = center
                aligned = pickup._aligning(center)
                if aligned:  # only True when already within tolerance
                    print("[BallInHole] Aligned, transitioning to APPROACHING_BALL")
                    self.state = 4

            elif self.state == 4:
                reached = pickup._approaching() # approach to the golf ball
                if reached:
                    service.send("robobot/cmd/ti", "rc 0 0")
                    self.state = 5
                    print(f"[BallInHole] Ball in reach, transitioning to PICKING_UP")

            elif self.state == 5:
                pickup._picking_up() # pick up the golf ball
                # Keep the arm down for robot balance
                print(f"[BallInHole] Ball picked up, transitioning to NAVIGATING_HOLE")
                #service.send("robobot/cmd/T0", "servo 1 657 100")  # Lower gripper down
                self.state = 6

            elif self.state == 6:
                pose.tripBreset()
                edge.lineControl(0.04, followLeft=False) # slowly move down the see saw
                self.state = 11 

            elif self.state == 11:
                
                if pose.tripBtimePassed() > 7:
                    #service.send("robobot/cmd/T0", "servo 1 -400 100")
                    pose.tripBreset()
                    edge.lineControl(0.15, followLeft=False)
                    # accelerate from 0.04m/s to 0.15m/s for saving time 
                    service.send("robobot/cmd/T0", "servo 1 600 100")
                    #Slightly raise arm
                    self.state = 12 

            elif self.state == 12:
                if pose.tripB > 0.3:
                    service.send("robobot/cmd/T0", "servo 1 -400 150") #raise the arm
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

