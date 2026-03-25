from ball_tracking import ball_tracking
from scam import cam
import time
from uservice import service
from scam_calibration import CameraCalib

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
        self.execute()


    def execute(self):
        '''Start functionality'''
        while not service.stop:

            if self.state == self.SEARCHING:
                ok, img = self.get_img()
                if not ok:
                    time.sleep(0.05)
                    continue

                center, radius = self._searching_golf_ball(img)

                if center is not None:
                    self.ball_center = center  # store for next states
                    self.ball_radius = radius
                    print(f"[BallInHole] Ball found at {center}, transitioning to ALIGNING")
                    self.state = self.ALIGNING
                else:
                    # No ball yet — rotate slowly to scan
                    service.send("robobot/cmd/ti", "rc 0 0.2")

            elif self.state == self.ALIGNING:
                ok, img = self.get_img()
                if not ok:
                    time.sleep(0.05)
                    continue

                # Re-detect on fresh frame so alignment is reactive
                center, radius = self._searching_golf_ball(img)
                if center is None:
                    # Lost the ball, go back to search
                    print(f"[BallInHole] Lost ball during alignment, back to SEARCHING")
                    self.state = self.SEARCHING
                    continue

                self.ball_center = center  # keep updating with fresh position
                aligned = self._aligning(center, img)

                if aligned:
                    service.send("robobot/cmd/ti", "rc 0 0")
                    print(f"[BallInHole] Aligned, transitioning to APPROACHING")
                    self.state = self.APPROACHING

            elif self.state == self.APPROACHING:
                reached = self._approaching()

                if reached:
                    service.send("robobot/cmd/ti", "rc 0 0")
                    print(f"[BallInHole] Ball in reach, transitioning to PICKING_UP")
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


    def get_img(self, trys=0):
        '''get image from rasp camera and return it also undistorted via calibration'''
        try:
            ok, img, imgTime = cam.getImage()
        except Exception as e:
            print(f"Error getting image: {e}")
            trys += 1
            if trys >= 3:
                print(f"Max attempts reached")
                return None
            time.sleep(0.2)
            return self.get_img(trys)
        
        undistorted_img = CameraCalib.undistort(img)
        return undistorted_img

    def _searching_golf_ball(self,img):
        '''Searching for the golf ball'''
        center, radius = ball_tracking(img,display = True)
        return center
    

    def _aligning(self,last_center):
        '''Steer robot such the ball center is centered in frame for x-axis'''

        

    def _approaching(self,at_end = False):
        '''Driving towards ball, maybe parallel thread with camera input?'''
        if at_end == True:
            self.state = 3
            return
        self.searching


    def _picking_up(self):
        '''Pick up golf ball with servo arms and CV'''
        pass


    def _navigating_hole(self):
        '''Drive to hole with no line following'''
        pass


    def _dropping(self):
        '''Open servo to release ball into hole'''
        pass


    def _record_start_pose(self):
        '''Get initial pose '''
        pass