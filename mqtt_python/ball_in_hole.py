from ball_tracking import ball_tracking
from hole_detection import hole_tacking
from qr_detection import qr_tacking
from scam import cam
import time
from uservice import service
from scam_calibration import CameraCalib
import cv2
from sedge import edge
from spose import pose
from sir import ir


def sleep(t):
    start = time.time()
    while (time.time() - start < t) and not service.stop:
        time.sleep(0.01)


class BallInHole:
    SEARCHING_BALL = 0
    ALIGNING_BALL = 1
    APPROACHING_BALL = 2
    PICKING_UP_GOLF_BALL = 3
    NAVIGATING_HOLE = 4
    ALIGNING_HOLE = 5
    APPROACHING_HOLE = 6
    DROPPING = 7
    BACK_TO_LINE = 8
    DONE = 9

    # Extra time from mission panner
    # go back to line
    KNOCK_CUP = 10  # can use gripper or high speed crash
    SEARCHING_BLUE = 11
    ALIGNING_QR_C = 12
    APPROACHING_QR_C = 13
    SEARCHING_RED = 14
    ALIGNING_QR_B = 15
    APPROACHING_QR_B = 16

    def __init__(self, ball_color):
        self.state = 0
        self.in_center = False
        self.final_alignment = False
        self.calib = CameraCalib()
        pose.tripBreset()
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
            sleep(0.2)
        print(
            "[BallInHole] WARNING: Camera not ready after timeout, proceeding anyway."
        )

    def ball_pick_up(self):
        """Find, approach and pick up the ping pong ball"""
        self.state = self.SEARCHING_BALL

        while not service.stop:
            if self.state == self.SEARCHING_BALL:
                img = self.get_img()

                print("###################################################")

                center, radius = self._searching_golf_ball(img, self.ball_color)

                # cv2.imshow("BallInHole Search", img)
                if center is not None:
                    service.send("robobot/cmd/ti", "rc 0 0")
                    sleep(0.5)
                    self.ball_center = center  # store for next states
                    self.ball_radius = radius
                    print("###################################################")
                    print(
                        f"[BallInHole] Ball found at {center}, transitioning to ALIGNING_BALL"
                    )
                    print("###################################################")
                    self.state = self.ALIGNING_BALL

                else:
                    # No ball yet — rotate slowly to scan
                    service.send("robobot/cmd/ti", "rc 0 0.2")

            elif self.state == self.ALIGNING_BALL:
                # img = self.get_img(trys = 10)

                img = self.get_img()
                center, radius = self._searching_golf_ball(img, self.ball_color)
                if center is None:
                    service.send("robobot/cmd/ti", "rc 0 0")
                    sleep(0.3)
                    print(
                        "[BallInHole] Lost ball during alignment, back to SEARCHING_BALL"
                    )
                    self.state = self.SEARCHING_BALL
                    continue

                self.ball_center = center
                aligned = self._aligning(center)  # does one timed correction

                if aligned:  # only True when already within tolerance
                    print("[BallInHole] Aligned, transitioning to APPROACHING_BALL")
                    self.state = self.APPROACHING_BALL

            elif self.state == self.APPROACHING_BALL:
                reached = self._approaching()

                if reached:
                    service.send("robobot/cmd/ti", "rc 0 0")
                    if self.final_alignment == False:
                        print("#####################")
                        print("CHECKING FINAL ALLIGNMENT")
                        print("#####################")
                        self.state = self.ALIGNING_BALL
                        self.final_alignment = True
                    self.state = self.PICKING_UP_GOLF_BALL
                    print(f"[BallInHole] Ball in reach, transitioning to PICKING_UP")

            elif self.state == self.PICKING_UP_GOLF_BALL:
                self._picking_up()
                print(f"[BallInHole] Ball picked up, transitioning to NAVIGATING_HOLE")
                self.state = self.DONE

            elif self.state == self.DONE:
                break

    def ball_drop_down(self):
        """Find and approach the hole, drop the ping pong ball"""
        self.state = self.ALIGNING_HOLE

        while not service.stop:
            if self.state == self.ALIGNING_HOLE:
                img = self.get_img()
                center_hole = self._searching_hole(img)
                if center_hole is None:
                    # No hole yet — rotate slowly to scan
                    service.send("robobot/cmd/ti", "rc 0 0.2")
                    continue
                aligned = self._aligning(center_hole)

                if aligned:
                    print("Hole Aligned, approaching hole")
                    self.state = self.APPROACHING_HOLE

            elif self.state == self.APPROACHING_HOLE:
                approach_hole = self._approaching_hole()
                if approach_hole:
                    service.send("robobot/cmd/ti", "rc 0 0")
                    print("hole approached, going to drop")
                    self.state = self.DROPPING

            elif self.state == self.DROPPING:
                self._dropping()
                self.state = self.DONE

            elif self.state == self.DONE:
                break

    def ball_drop_down_grid_C(self):
        """Find and approach the grid, drop the ball"""
        self.state = self.ALIGNING_QR_C

        while not service.stop:
            if self.state == self.ALIGNING_QR_C:
                img = self.get_img()
                center_qr_c = self._searching_qr_C(img)
                if center_qr_c is None:
                    # scan if lost
                    service.send("robobot/cmd/ti", "rc 0 0.2")
                    continue
                aligned = self._aligning(center_qr_c)

                if aligned:
                    print("Hole Aligned, approaching hole")
                    self.state = self.APPROACHING_QR_C

            elif self.state == self.APPROACHING_QR_C:
                approach_hole = self._approaching_qr_c()
                if approach_hole:
                    service.send("robobot/cmd/ti", "rc 0 0")
                    print("hole approached, going to drop")
                    self.state = self.DROPPING

            elif self.state == self.DROPPING:
                self._dropping()
                self.state = self.DONE

            elif self.state == self.DONE:
                break

    def ball_drop_down_grid_B(self):
        """Find and approach the grid, drop the ball"""
        self.state = self.ALIGNING_QR_B

        while not service.stop:
            if self.state == self.ALIGNING_QR_B:
                img = self.get_img()
                center_hole = self._searching_qr_B(img)
                if center_hole is None:
                    # scan if lost
                    service.send("robobot/cmd/ti", "rc 0 0.2")
                    continue
                aligned = self._aligning(center_hole)

                if aligned:
                    print("Hole Aligned, approaching hole")
                    self.state = self.APPROACHING_QR_B

            elif self.state == self.APPROACHING_QR_B:
                approach_hole = self._approaching_qr_B()
                if approach_hole:
                    service.send("robobot/cmd/ti", "rc 0 0")
                    print("hole approached, going to drop")
                    self.state = self.DROPPING

            elif self.state == self.DROPPING:
                self._dropping()
                self.state = self.DONE

            elif self.state == self.DONE:
                break

    def knock_down_cup(self):
        while not service.stop:
            if ir.ir[1] < 1:
                sleep(0.8)
                edge.lineControl(0.0)
                service.send("robobot/cmd/ti", f"rc 0.0 0.0")
                sleep(0.5)
                service.send("robobot/cmd/ti", f"rc -0.2 0.0")
                sleep(1)
                service.send("robobot/cmd/ti", f"rc 0.0 -0.2")
                sleep(3)
                service.send("robobot/cmd/ti", f"rc 0.2 0.0")
                sleep(3)
                service.send("robobot/cmd/ti", f"rc 0.0 0.2")
                sleep(3)
                return

    def get_img(self):
        """get image from rasp camera and return it also undistorted via calibration"""
        if cam.useCam:
            ok, img, imgTime = cam.getImage()
            if not ok:  # size(img) == 0):
                if cam.imageFailCnt < 5:
                    print("% Failed to get image.")
        return img
        # else:
        #     return self.calib.undistort(img.copy())

    def _searching_golf_ball(self, img, ball_color):
        """Searching for the golf ball"""
        center, radius = ball_tracking(img, display=False, ball_color=ball_color)
        return center, radius

    def _aligning(
        self, center
    ):  # TODO: Need to adjust this such that it doesn't get stuck on minor adjustments
        """Steer robot such the ball center is centered in frame for x-axis"""
        TARGET_X = 288
        TURN_RATE = 0.5
        TOLERANCE = 0.025

        # angle_x, _ = self.calib.pixel_to_angle(center[0], center[1])
        # target_angle_x, _ = self.calib.pixel_to_angle(TARGET_X, center[1])
        # angle_error = angle_x - target_angle_x

        # if abs(angle_error) < TOLERANCE:
        #      service.send("robobot/cmd/ti", "rc 0 0")
        #     return True

        # turn_time = abs(angle_error) / TURN_RATE
        # turn = -TURN_RATE if angle_error > 0 else TURN_RATE
        # service.send("robobot/cmd/ti", f"rc 0 {turn}")

        # start = time.time()
        # while (time.time() - start < turn_time) and not service.stop:
        #     time.sleep(0.01)

        # service.send("robobot/cmd/ti", "rc 0 0")
        # return False  # return False so execute re-detects and verifies

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

    def _approaching_hole(self, at_end=False):
        """Driving towards ball, maybe parallel thread with camera input?"""
        TARGET_Y = 385
        TOLERANCE_Y = 15  # pixels, tune this

        img = self.get_img()
        if img is None:
            return False

        center_hole = self._searching_hole(img)
        if center_hole is None:
            return False

        error_y = (
            TARGET_Y - center_hole[1]
        )  # positive = ball too far (low y), need to drive forward
        print(
            f"[Approaching] hole  y={center_hole[1]}, target y={TARGET_Y}, error={error_y}"
        )

        if abs(error_y) < TOLERANCE_Y:
            return True  # reached pickup position

        service.send("robobot/cmd/ti", "rc 0.07 0")
        return False

    def _approaching_qr_c(self, at_end=False):
        """Driving towards ball, maybe parallel thread with camera input?"""
        TARGET_Y = 385
        TOLERANCE_Y = 60  # pixels, tune thiss

        img = self.get_img()
        if img is None:
            return False

        center_qr_c = self._searching_qr_C(img)
        if center_qr_c is None:
            return False

        error_y = (
            TARGET_Y - center_qr_c[1]
        )  # positive = ball too far (low y), need to drive forward
        print(
            f"[Approaching] qr  y={center_qr_c[1]}, target y={TARGET_Y}, error={error_y}"
        )

        if abs(error_y) < TOLERANCE_Y:
            return True  # reached pickup position

        service.send("robobot/cmd/ti", "rc 0.07 0")
        return False

    def _approaching_qr_B(self, at_end=False):
        """Driving towards ball, maybe parallel thread with camera input?"""
        TARGET_Y = 385
        TOLERANCE_Y = 60  # pixels, tune thiss

        img = self.get_img()
        if img is None:
            return False

        center_qr_B = self._searching_qr_B(img)
        if center_qr_B is None:
            return False

        error_y = (
            TARGET_Y - center_qr_B[1]
        )  # positive = ball too far (low y), need to drive forward
        print(
            f"[Approaching] qr  y={center_qr_B[1]}, target y={TARGET_Y}, error={error_y}"
        )

        if abs(error_y) < TOLERANCE_Y:
            return True  # reached pickup position

        service.send("robobot/cmd/ti", "rc 0.07 0")
        return False

    def _approaching(self, at_end=False):
        """Driving towards ball, maybe parallel thread with camera input?"""
        TARGET_Y = 357
        TOLERANCE_Y = 20  # pixels, tune this

        img = self.get_img()
        if img is None:
            return False

        center, radius = self._searching_golf_ball(img, self.ball_color)
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

    def _picking_up(self):
        """Pick up golf ball with servo arms and CV"""

        sleep(0.5)
        service.send("robobot/cmd/T0", "servo 1 657 100")  # Lower gripper down
        sleep(2)
        service.send(
            "robobot/cmd/T0", "servo 2 400 150"
        )  # close gripper ### to open its -200
        sleep(2)
        service.send("robobot/cmd/T0", "servo 1 -400 100")  # raise gripper

    def _searching_hole(self, img):
        """Searching for the hole"""
        center_hole = hole_tacking(img)
        return center_hole

    def _searching_qr_C(self, img):
        """Searching fot the QR"""
        center_qr = qr_tacking(img, "C")
        return center_qr

    def _searching_qr_B(self, img):
        """Searching fot the QR"""
        center_qr = qr_tacking(img, "B")
        return center_qr

    def _dropping(self):
        """Open servo to release ball into hole"""
        sleep(0.5)
        service.send("robobot/cmd/T0", "servo 1 650 100")  # Lower gripper down
        sleep(2)
        service.send(
            "robobot/cmd/T0", "servo 2 -200 150"
        )  # close gripper ### to open its -200
        sleep(2)
        service.send("robobot/cmd/T0", "servo 1 -400 100")  # raise gripper

    def _record_start_pose(self):
        """Get initial pose"""
        pass

