import cv2
import sys
import numpy as np
from scam import cam
from uservice import service
from setproctitle import setproctitle

"""
hole detector draft script, with various params to tune
so that we can detect the exact hole in asta. 

TO DO param tuning for holes in asta
"""

detector = cv2.SimpleBlobDetector_create()
params = cv2.SimpleBlobDetector_Params()

params.minThreshold = 10
params.maxThreshold = 210
params.thresholdStep = 10

# params.filterByArea = True
params.minArea = 170
# params.maxArea = 40000

# params.filterByCircularity = True
params.minCircularity = 0.25

# params.filterByConvexity = False
# params.minConvexity = 0.87

# params.filterByInertia = True
# params.minInertiaRatio = 0.8

params.minDistBetweenBlobs = 2000

# Create a detector with the parameters
detector = cv2.SimpleBlobDetector_create(params)


def loop():
    while not (service.stop):
        ok, im, imgTime = cam.getImage()
        overlay = im.copy()

        keypoints = detector.detect(im)
        for k in keypoints:
            cv2.circle(
                overlay, (int(k.pt[0]), int(k.pt[1])), int(k.size / 2), (0, 0, 255), -1
            )
            print(f"x_hole: {k.pt[0]}, y_hole {k.pt[1]}")
        opacity = 0.5
        cv2.addWeighted(overlay, opacity, im, 1 - opacity, 0, im)


if __name__ == "__main__":
    if service.process_running("mqtt-client"):
        print("% mqtt-client is already running - terminating")
        print("%   if it is partially crashed in the background, then try:")
        print("%     pkill mqtt-client")
        print("%   or, if that fails use the most brutal kill")
        print("%     pkill -9 mqtt-client")
    else:
        setproctitle("mqtt-client")
        print("% Starting")
        service.setup("localhost")  # localhost
        if service.connected:
            loop()
        service.terminate()
    print("% Main Terminated")
