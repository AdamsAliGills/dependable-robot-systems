from ball_tracking import ball_tracking
from scam import cam
import time
from uservice import service
class BallInHole():

    SEARCHING = 0
    ALIGNING = 1
    APPORACHING = 2
    PICKING_UP_GOLF_BALL = 3
    NAVIGATING_HOLE = 4
    DROPPING = 5
    DONE = 6


    def __init__(self):
        self.state = 0

    def execute(self):
        '''Start functionality'''
        if self.state == 0: #searching
            img = self.get_img()
            if img == None:
                self.state = 99
            center = self._searching_golf_ball(img)
            if center:
                self.state = 1
        elif self.state == 99:
            return 


    def step(self):
        '''State machine for states'''
        pass

    def get_img(self,trys):
        try: 
            ok, img, imgTime = cam.getImage()
        except Exception as e:
            print(f"Error in getting image from Rasp: {e}")
            trys +=1 
        if trys == 3:
            print(f"Error in getting images from Rasp: {e}, attempts met {trys}")
            return None
        time.sleep(0.2) #Abitrary number

    def _searching_golf_ball(self,img):
        '''Searching for the golf ball'''
        center, radius = ball_tracking(img)
        return center
    
    def _aligning(self):
        '''Steer robot such the ball center is centered in frame'''
        pass

    def _approaching(self):
        '''Driving towards ball with CV'''
        pass

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