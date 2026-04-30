from uservice import service
from round_about import roundAbout
from sedge import edge
import math
import cv2
from ball_tracking import ball_tracking
from detection_utils import (
    wait_ramp_bottom,
    wait_ramp_top,
    wait_turn,
    wait_end,
    wait_line,
)
from sir import ir
import time
from scam import cam
from ball_in_hole import BallInHole
# from balls_in_grid import BallsInGrid

LONG_RAMP_TILT = 8  # TODO check real value
SHORT_RAMP_TILT = 15  # TODO check real value


def sleep(t):
    start = time.time()
    while (time.time() - start < t) and not service.stop:
        time.sleep(0.01)


class missionPlanner:
    def __init__(self):
        self.planMission()

        # ball_o = BallInHole("red")
        # ball_o.ball_pick_up()

    def planMission(self):
        edge.lineControl(0.2, False)
        sleep(2)

        # ball_blue = BallInHole("blue")
        # ball_blue.knock_down_cup_right()
        # ball_blue.ball_pick_up()
        # ball_blue.ball_drop_down_grid_C()
        # ball_red = BallInHole("red")
        # ball_red.ball_pick_up()
        # service.send("robobot/cmd/ti", "rc 0 -0.6")
        # sleep(3)
        # ball_red.ball_drop_down_grid_B()

        ball_o = BallInHole("orange")
        ball_o.knock_cup()

            

        ok, img, imgTime = cam.getImage()
        center_red, radius_red = ball_tracking(img, display=True, ball_color="red")
        center_blue, radius_blue = ball_tracking(img, display=True, ball_color="blue")

        turn_direction,color = self.compare_positions(center_red, center_blue)
        print("#################################################")
        print(f"turn direction: {turn_direction}, color: {color}")
        print("#################################################")

        ball_o = BallInHole(color)
        print("finished initalization")
        if turn_direction == "right":
            ball_o.knock_down_cup_right()
        else:
            ball_o.knock_down_cup_left()
        print("#################################################")
        print("going to pick up ")
        print("#################################################")

        ball_o.ball_pick_up()

        # To face the grid quicker

        if turn_direction == "right":
            service.send("robobot/cmd/ti", "rc 0 -0.2")
            time.sleep(2)
            service.send("robobot/cmd/ti", "rc 0 0")

        elif turn_direction == "left":
            service.send("robobot/cmd/ti", "rc 0 0.2")
            time.sleep(2)
            service.send("robobot/cmd/ti", "rc 0 0")
        service.send("robobot/cmd/T0", "servo 2 0 100")  # open gripper
        
        if color == "blue": #TODO: Make this into a function to avoid code duplication
            if turn_direction == "right":
                ball_o.ball_drop_down_grid_C(drop_flag=True)
            else:
                ball_o.ball_drop_down_grid_B(drop_flag=False)
        
        elif color == "red":
            if turn_direction == "right":
                ball_o.ball_drop_down_grid_C(drop_flag=False)
            else:
                ball_o.ball_drop_down_grid_B(drop_flag=True)

        service.send("robobot/cmd/ti", "rc -0.3 0") #Turn around after dropping ball off
        sleep(3)
        service.send("robobot/cmd/ti", "rc 0 0") #Turn around after dropping ball off

        service.send("robobot/cmd/ti", "rc 0 -0.2") #Turn around after dropping ball off
        time.sleep(3.5)
        service.send("robobot/cmd/ti", "rc 0 0")

        colors = ["red","blue"]
        colors.remove(color)
        colors_left = colors[0]
        ball_o = BallInHole(colors_left)
        ball_o.ball_pick_up()
        
        service.send("robobot/cmd/ti", "rc 0 0.4") #Turn around after dropping ball off
        time.sleep(3.5)

        if colors_left == "blue": #TODO: Make this into a function to avoid code duplication
            if turn_direction == "right":
                ball_o.ball_drop_down_grid_C(drop_flag=True)
            else:
                ball_o.ball_drop_down_grid_B(drop_flag=False)
        
        elif colors_left == "red":
            if turn_direction == "right":
                ball_o.ball_drop_down_grid_B(drop_flag=True)
            else:
                ball_o.ball_drop_down_grid_C(drop_flag=False)

        # rotate over the balls
        # qr detection
        # ball detection
        # qr detection
        # back on line

    def compare_positions(self, center_red, center_blue):
        if center_red is None and center_blue is None:  # no balls detected
            turn_direction = "right"
            color = "red"
        elif center_red is not None and center_blue is not None:  # both balls detected
            edge_ball, side_red, side_blue = self.closer_to_edge(
                center_red[0], center_blue[0]
            )
            if edge_ball == center_red[0]:
                turn_direction = side_red
                color = "red"
            elif edge_ball == center_blue[0]:
                turn_direction = side_blue
                color = "blue"
        elif center_red is not None and center_blue is None:  # only red ball detected
            edge_ball, side_red = self.closer_to_edge(center_red[0], None)
            turn_direction = side_red
            color = "red"

        else:  # only blue ball detected
            edge_ball, side_blue = self.closer_to_edge(None, center_blue[0])
            turn_direction = side_blue
            color = "blue"
        return turn_direction, color

    def closer_to_edge(self, x1, x2):
        center_x = 300  # Assuming image width is 640 pixels

        def side_of(x):
            return "right" if x > center_x else "left"

        # Handle None cases
        if x1 is None and x2 is None:
            print("Both values are None")
            return None, None

        if x1 is None:
            side2 = side_of(x2)
            print(f"x1 is None, x2={x2} is to the {side2} of center")
            return x2, side2

        if x2 is None:
            side1 = side_of(x1)
            print(f"x2 is None, x1={x1} is to the {side1} of center")
            return x1, side1

        # Both present — original logic
        dist1 = abs(x1 - center_x)
        dist2 = abs(x2 - center_x)

        closer = x1 if dist1 > dist2 else x2
        side1 = side_of(x1)
        side2 = side_of(x2)

        print(f"x1={x1} is to the {side1} of center")
        print(f"x2={x2} is to the {side2} of center")
        print(f"x{'1' if closer == x1 else '2'}={closer} is closer to the edge")

        return closer, side1, side2


if __name__ == "__main__":
    mp = missionPlanner()

