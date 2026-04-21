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
    ADDITIONAL_TIME = 0
    KNOCK_BALLS = 1  #
    INITIAL_CORNER_POS = 2  #
    APPROACHING_BALL_BLUE = 3  # kris
    PICKING_UP_BALL_BLUE = 4  # kris
    NAVIGATING_GRID_C = 5  # adam
    RAMP_CORNER_POS = 6  # adam
    APPROACHING_BALL_RED = 7  # kris
    PICKING_UP_BALL_RED = 8  # kris
    # WILL GO BACK TO RAMP CORNER
    NAVIGATING_GRID_B = 9  # adam
    BACK_TO_LINE = 10  # adam
    DONE = 11  # adam

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

    def additional_time(self):
        pose.tripBreset()
        service.send("robobot/cmd/ti", "rc 0.2 0.0")
        if pose.tripB > 2.7:
            service.send("robobot/cmd/ti", "rc 0.0 -0.7")
            time.sleep(1)
            service.send("robobot/cmd/ti", "rc 0.1 0.0")
            time.sleep(0.15)
            service.send("robobot/cmd/ti", "rc -0.1 0.0")
            time.sleep(0.15)
        else:
            print(
                f"# drive 1.95m drove {pose.tripB:.3f}m in {pose.tripBtimePassed():.3f} seconds"
            )
