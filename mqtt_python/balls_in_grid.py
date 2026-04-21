from ball_tracking import ball_tracking
from hole_detection import hole_tacking
from scam import cam
import time
from uservice import service
from scam_calibration import CameraCalib
import cv2
from sedge import edge
from spose import pose


def sleep(t):
    start = time.time()
    while (time.time() - start < t) and not service.stop:
        time.sleep(0.01)


class BallsInGrid:
    KNOCK_BALLS = 0  #
    INITIAL_CORNER_POS = 1  #
    APPROACHING_BALL_BLUE = 2  # kris
    PICKING_UP_BALL_BLUE = 3  # kris
    NAVIGATING_GRID_C = 4  # adam
    RAMP_CORNER_POS = 5  # adam
    APPROACHING_BALL_RED = 6  # kris
    PICKING_UP_BALL_RED = 7  # kris
    # WILL GO BACK TO RAMP CORNER
    NAVIGATING_GRID_B = 8  # adam
    BACK_TO_LINE = 9  # adam
    DONE = 10  # adam

    def __init__(self):
        self.state = 0
        self.in_center = False
        self.final_alignment = False
        self.calib = CameraCalib()
        pose.tripBreset()

    def _wait_for_camera(self, timeout=10.0):
        """Block until camera produces a valid frame or timeout."""
        print("[BallsInGrid] Waiting for camera...")
        start = time.time()
        while time.time() - start < timeout:
            ok, img, _ = cam.getImage()
            if ok and img is not None:
                print("[BallsInGrid] Camera ready.")
                return
            sleep(0.2)
        print(
            "[BallsInGrid] WARNING: Camera not ready after timeout, proceeding anyway."
        )
