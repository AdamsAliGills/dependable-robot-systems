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

low_H = 6
high_H = 30
low_S = 40
high_S = 160
low_V = 40
high_V = 200

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


def hole_tacking(img):
    frame = img[int(img.shape[0] / 2) : int(img.shape[0])]
    frame = cv2.GaussianBlur(frame, (5, 5), 0)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    frame = cv2.inRange(frame, (low_H, low_S, low_V), (high_H, high_S, high_V))

    keypoints = detector.detect(frame)
    largest_size = 0
    largest_keypoint = None
    for keypoint in keypoints:
        if keypoint.size > largest_size:
            largest_size = keypoint.size
            largest_keypoint = keypoint
    if largest_keypoint:
        print(largest_keypoint.pt)
    return largest_keypoint


"""
def loop():
    while not (service.stop):
        ok, frame, imgTime = cam.getImage()
        if frame is None:
            break

        frame = cv2.GaussianBlur(frame, (5, 5), 0)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame = cv2.inRange(frame, (low_H, low_S, low_V), (high_H, high_S, high_V))
        keypoints = detector.detect(frame)
        largest_size = 0
        largest_keypoint = None
        for keypoint in keypoints:
            if keypoint.size > largest_size:
                largest_size = keypoint.size
                largest_keypoint = keypoint
        if largest_keypoint:
            print(largest_keypoint.pt)
        frame = cv2.drawKeypoints(
            frame, keypoints, 0, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
        )
        cv2.imshow("result", frame)

        key = cv2.waitKey(30)
        if key == ord("q"):
            break


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
    """
