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
        self.execute()

    def execute(self):
        '''Start functionality'''
        if self.state == 0: #searching
            img = self.get_img()
            # if img == None:
            #     self.state = 99
            center = self._searching_golf_ball(img)
            if center:
                self.state = 1
        if self.state == 2:
            self.approaching(center)
            
        

        


    def step(self):
        '''State machine for states'''
        pass

    def get_img(self, trys=0):
        try:
            ok, img, imgTime = cam.getImage()
            return img
        except Exception as e:
            print(f"Error getting image: {e}")
            trys += 1
            if trys >= 3:
                print(f"Max attempts reached")
                return None
            time.sleep(0.2)
            return self.get_img(trys)

    def _searching_golf_ball(self,img):
        '''Searching for the golf ball'''
        center, radius = ball_tracking(img,display = True)
        return center
    
    def _aligning(self):
        '''Steer robot such the ball center is centered in frame'''
        center = self._searching_golf_ball(img)



    def _approaching(self,at_end = False):
        '''Driving towards ball with CV'''
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