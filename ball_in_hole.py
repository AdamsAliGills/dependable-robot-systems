
class BallInHole():

    SEARCHING = 0
    ALIGNING = 1
    APPORACHING = 2
    PICKING_UP_GOLF_BALL = 3
    NAVIGATING_HOLE = 4
    DROPPING = 5
    DONE = 6


    def __init__(self):
        pass

    def execute(self):
        '''Start functionality'''
        pass

    def step(self):
        '''State machine for states'''
        pass

    def _searching_golf_ball(self):
        '''Searching for the golf ball'''
        pass

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