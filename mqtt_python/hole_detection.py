import cv2
import sys
import numpy as np

"""
hole detector draft script, with various params to tune
so that we can detect the exact hole in asta. 

TO DO param tuning for holes in asta
"""
camera = cv2.VideoCapture(0)

detector = cv2.SimpleBlobDetector_create()
params = cv2.SimpleBlobDetector_Params()

params.minThreshold = 10
params.maxThreshold = 200
params.thresholdStep = 15

# params.filterByArea = True
params.minArea = 150
# params.maxArea = 40000

# params.filterByCircularity = True
params.minCircularity = 0.75

# params.filterByConvexity = False
# params.minConvexity = 0.87

# params.filterByInertia = True
# params.minInertiaRatio = 0.8

params.minDistBetweenBlobs = 185

# Create a detector with the parameters
detector = cv2.SimpleBlobDetector_create(params)

while camera.isOpened():
    retval, im = camera.read()
    overlay = im.copy()

    keypoints = detector.detect(im)
    for k in keypoints:
        cv2.circle(
            overlay, (int(k.pt[0]), int(k.pt[1])), int(k.size / 2), (0, 0, 255), -1
        )
        print(f"x_hole: {k.pt[0]}, y_hole {k.pt[1]}")
    opacity = 0.5
    cv2.addWeighted(overlay, opacity, im, 1 - opacity, 0, im)

    cv2.imshow("Output", im)

    k = cv2.waitKey(1) & 0xFF
    if k % 256 == 27:
        break

camera.release()
cv2.destroyAllWindows()
