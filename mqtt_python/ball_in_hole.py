from ball_tracking import ball_tracking
from scam import cam
import time
from uservice import service
from scam_calibration import CameraCalib
import cv2
class BallInHole():

    SEARCHING = 0
    ALIGNING = 1
    APPROACHING = 2
    PICKING_UP_GOLF_BALL = 3
    NAVIGATING_HOLE = 4
    DROPPING = 5
    DONE = 6

    
    def __init__(self):
        self.state = 0
        self.in_center = False
        self.calib = CameraCalib()
        time.sleep(3)
        service.send("robobot/cmd/T0", "servo 1 -400 50")

        self.execute() 
    def sleep(t):
        start = time.time()
        while (time.time() - start < t) and not service.stop:
            time.sleep(0.01)
    
    
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
        print("[BallInHole] WARNING: Camera not ready after timeout, proceeding anyway.")
    
    
    def execute(self):
        '''Start functionality'''
        while not service.stop:

            if self.state == self.SEARCHING:
                img = self.get_img()
              
                print("###################################################")
            
                center, radius = self._searching_golf_ball(img)
                



                # cv2.imshow("BallInHole Search", img)
                if center is not None:
                    service.send("robobot/cmd/ti", "rc 0 0")
                    time.sleep(0.5)
                    self.ball_center = center  # store for next states
                    self.ball_radius = radius
                    print("###################################################")
                    print(f"[BallInHole] Ball found at {center}, transitioning to ALIGNING")
                    print("###################################################")
                    self.state = self.ALIGNING

                else:
                    # No ball yet — rotate slowly to scan
                    service.send("robobot/cmd/ti", "rc 0 0.2")

            elif self.state == self.ALIGNING:
                # img = self.get_img(trys = 10)
              
                img = self.get_img()
                center, radius = self._searching_golf_ball(img)
                if center is None:
                    service.send("robobot/cmd/ti", "rc 0 0")
                    time.sleep(0.3)
                    print("[BallInHole] Lost ball during alignment, back to SEARCHING")
                    self.state = self.SEARCHING
                    continue

                self.ball_center = center
                aligned = self._aligning(center)  # does one timed correction

                if aligned:  # only True when already within tolerance
                    print("[BallInHole] Aligned, transitioning to APPROACHING")
                    self.state = self.APPROACHING
                
                
                
                
                
                
        
            elif self.state == self.APPROACHING:
                reached = self._approaching()

                if reached:
                    service.send("robobot/cmd/ti", "rc 0 0")
                    print(f"[BallInHole] Ball in reach, transitioning to PICKING_UP")
                    time.sleep(2)
                    self.state = self.PICKING_UP_GOLF_BALL

            elif self.state == self.PICKING_UP_GOLF_BALL:
                self._picking_up()
                print(f"[BallInHole] Ball picked up, transitioning to NAVIGATING_HOLE")
                self.state = self.NAVIGATING_HOLE

            elif self.state == self.NAVIGATING_HOLE:
                reached = self._navigating_hole()

                if reached:
                    service.send("robobot/cmd/ti", "rc 0 0")
                    print(f"[BallInHole] At hole, transitioning to DROPPING")
                    self.state = self.DROPPING

            elif self.state == self.DROPPING:
                self._dropping()
                print(f"[BallInHole] Ball dropped, DONE")
                self.state = self.DONE

            elif self.state == self.DONE:
                break

            time.sleep(0.05)
            


    def step(self):
        '''State machine for states'''
        pass


    def get_img(self):
        '''get image from rasp camera and return it also undistorted via calibration'''
        if cam.useCam:
            ok, img, imgTime = cam.getImage()
            if not ok: # size(img) == 0):
                if cam.imageFailCnt < 5:
                    print("% Failed to get image.")
        return img
            # else:
            #     return self.calib.undistort(img.copy())

    def _searching_golf_ball(self,img):
        '''Searching for the golf ball'''
        center, radius = ball_tracking(img,display = False)
        return center,radius
    

    def _aligning(self,center): #TODO: Need to adjust this such that it doesn't get stuck on minor adjustments
        '''Steer robot such the ball center is centered in frame for x-axis'''
        TARGET_X = 284  
        TURN_RATE = 0.3
        TOLERANCE = 0.02

        angle_x, _ = self.calib.pixel_to_angle(center[0], center[1])
        target_angle_x, _ = self.calib.pixel_to_angle(TARGET_X, center[1])
        angle_error = angle_x - target_angle_x

        if abs(angle_error) < TOLERANCE:
            service.send("robobot/cmd/ti", "rc 0 0")
            return True

        turn_time = abs(angle_error) / TURN_RATE
        turn = -TURN_RATE if angle_error > 0 else TURN_RATE
        service.send("robobot/cmd/ti", f"rc 0 {turn}")

        # service-stop-aware sleep instead of time.sleep()
        start = time.time()
        while (time.time() - start < turn_time) and not service.stop:
            time.sleep(0.01)

        service.send("robobot/cmd/ti", "rc 0 0")
        return False  # return False so execute re-detects and verifies



    def _approaching(self,at_end = False):
        '''Driving towards ball, maybe parallel thread with camera input?'''
        TARGET_Y = 357
        TOLERANCE_Y = 30  # pixels, tune this

        img = self.get_img()
        if img is None:
            return False
        
        center, radius = self._searching_golf_ball(img)
        if center is None:
            return False
        
        error_y = TARGET_Y - center[1]  # positive = ball too far (low y), need to drive forward
        print(f"[Approaching] ball y={center[1]}, target y={TARGET_Y}, error={error_y}")

        if abs(error_y) < TOLERANCE_Y:
            return True  # reached pickup position
        
        service.send("robobot/cmd/ti", "rc 0.07 0")
        return False


    def _picking_up(self):
        '''Pick up golf ball with servo arms and CV'''
        
        time.sleep(1)
        service.send("robobot/cmd/T0", "servo 1 650 50")
        time.sleep(5)
        service.send("robobot/cmd/T0", "servo 1 3000 0")

    def _navigating_hole(self):
        '''Drive to hole with no line following'''
        pass


    def _dropping(self):
        '''Open servo to release ball into hole'''
        pass


    def _record_start_pose(self):
        '''Get initial pose '''
        pass