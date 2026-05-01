from uservice import service
from round_about import roundAbout
from guard_robot import GuardRobot
from see_saw import SeeSaw
from stair_climb import StairClimb
from sedge import edge
from detection_utils import wait_ramp_bottom, wait_ramp_top, wait_turn, wait_end, wait_line
import time
from scam import cam
from ball_in_hole import BallInHole

LONG_RAMP_TILT = 8 # TODO check real value
SHORT_RAMP_TILT = 15 # TODO check real value


def sleep(t):
    start = time.time()
    while (time.time() - start < t) and not service.stop:
        time.sleep(0.01)


class missionPlanner:
    def __init__(self):
        self.planMission()

    def planMission(self):
        
        edge.lineControl(0.2, followLeft=True)

        # initialize servos
        service.send("robobot/cmd/T0","servo 1 0 50")
        service.send("robobot/cmd/T0","servo 2 0 50")
        service.send("robobot/cmd/T0","servo 3 0 50")
        sleep(0.3)
        service.send("robobot/cmd/T0","servo 1 -400 50")
        service.send("robobot/cmd/T0","servo 2 0 50")
        service.send("robobot/cmd/T0","servo 3 265 50")
        
        wait_turn(25)
        sleep(1)

        edge.lineControl(0.05, followLeft=True)
        sleep(3)

        r = roundAbout(-135)
        r.execute()

        edge.lineControl(0.2, followLeft=False)
        sleep(3)
        wait_turn(80)
        print(f"TURN")
        stair_climb = StairClimb()
        stair_climb.execute()

    
        service.send("robobot/cmd/ti", f"rc 0.0 -0.7")
        wait_turn(85)
        service.send("robobot/cmd/ti", f"rc -0.1 0.0")
        sleep(1)
        service.send("robobot/cmd/ti", f"rc 0.2 0.0")
        wait_line()
        service.send("robobot/cmd/ti", f"rc 0.0 0.7")
        wait_turn(70)

        edge.lineControl(0.2, followLeft=False)
        sleep(3)
        see_saw = SeeSaw()
        see_saw.execute()

        service.send("robobot/cmd/ti", f"rc 0.0 0.7")
        wait_turn(95)
        service.send("robobot/cmd/ti", f"rc 0.2 0.0")
        wait_line()
        service.send("robobot/cmd/ti", f"rc 0.0 0.7")
        wait_turn(75)


        edge.lineControl(0.2, followLeft=False)
        sleep(1)
        wait_turn(80)
        print(f"FIRST TURN")
        sleep(2)
        wait_turn(75)
        print(f"SECOND TURN")
        edge.lineControl(0)
        
        service.send("robobot/cmd/ti", f"rc -0.15 0.0")
        sleep(8)

        service.send("robobot/cmd/ti", f"rc -0.1 -0.7")
        wait_turn(80)
        service.send("robobot/cmd/ti", f"rc 0.1 0.05")
        wait_end()
        service.send("robobot/cmd/ti", f"rc -0.1 0.0")
        sleep(2.6)
        service.send("robobot/cmd/ti", f"rc 0.0 -0.7")
        wait_turn(95)
        
        service.send("robobot/cmd/ti", f"rc 0.0 0.0")
        
        guard_robot = GuardRobot()
        guard_robot.execute()
        edge.lineControl(0.2, followLeft=False)

        wait_ramp_bottom(LONG_RAMP_TILT, tolerance = 3)
        print(f"START FIRST RAMP")
        edge.lineControl(0.3, followLeft=False)
        
        wait_ramp_top(LONG_RAMP_TILT, tolerance = 3)
        print(f"END FIRST RAMP")
        edge.lineControl(0.2, followLeft=False)
        sleep(2.5)
        edge.lineControl(0)
        service.send("robobot/cmd/ti", f"rc -0.05 -0.7")
        wait_turn(70)

        
        #service.send("robobot/cmd/ti", f"rc 0.0 -0.7")
        #sleep(0.3)
        service.send("robobot/cmd/ti", f"rc 0.0 0.0")
        
        ball_in_hole = BallInHole("orange")
        ball_in_hole.ball_drop_down()

        service.send("robobot/cmd/ti", f"rc 0.0 1.0")
        wait_turn(180)
        service.send("robobot/cmd/ti", f"rc 0.2 0.0")
        sleep(2)

        service.send("robobot/cmd/ti", f"rc 0.0 0.0")

        ball_in_hole.ball_pick_up()

        service.send("robobot/cmd/ti", f"rc 0.0 1.0")
        wait_turn(170) #TODO: It turns too far to the left
        service.send("robobot/cmd/ti", f"rc 0.2 0.0")
        sleep(2)
        service.send("robobot/cmd/ti", "rc 0.0 0.0")

        ball_in_hole.ball_drop_down()

        # back to line
        service.send("robobot/cmd/ti", "rc -0.07 0.0")
        wait_line()
        service.send("robobot/cmd/ti", "rc 0.0 0.7")
        wait_turn(80)
        edge.lineControl(0.2, True)

       
        print("DONE WITH BALL OP")
        wait_ramp_top(SHORT_RAMP_TILT, tolerance = 3)
        print(f"START SECOND RAMP")
        edge.lineControl(0.25, followLeft=False)

        wait_ramp_bottom(SHORT_RAMP_TILT, tolerance = 3)
        print(f"END SECOND RAMP")
        edge.lineControl(0.15, followLeft=True)

        #sleep(2.5)
        #edge.lineControl(0.0)

        #service.send("robobot/cmd/ti", f"rc 0.6 0.0")
        #sleep(2.5)
        #service.send("robobot/cmd/ti", f"rc 0.3 0.0")
        #sleep(0.5)
        #service.send("robobot/cmd/ti", f"rc 0.0 -0.7")
        #wait_turn(85)
        #service.send("robobot/cmd/ti", f"rc 0.1 0.0")
        #wait_end()
        #service.send("robobot/cmd/ti", f"rc 0.0 -0.7")
        #wait_turn(90)
        #service.send("robobot/cmd/ti", f"rc 0.6 0.0")
        #sleep(2.5)
        #service.send("robobot/cmd/ti", f"rc 0.4 0.0")
        #sleep(0.5)
        #service.send("robobot/cmd/ti", f"rc 0.0 -0.7")
        #wait_turn(85)
        #service.send("robobot/cmd/ti", f"rc 0.1 0.0")
        #wait_line()
        #service.send("robobot/cmd/ti", f"rc 0.0 -0.7")
        #wait_turn(85)
        #edge.lineControl(0.15, followLeft=True)

        wait_turn(80)
        print(f"TURN DETECTED")

        sleep(1.5)
        edge.lineControl(0)
        service.send("robobot/cmd/ti", f"rc 0.2 0.0")
        sleep(1)

        edge.lineControl(0.2, followLeft=True)

        sleep(3.5)

        edge.lineControl(0.05, followLeft=True)
        sleep(2)

        r = roundAbout(-225)
        r.execute()

        edge.lineControl(0.2, followLeft=True)
        wait_end()

