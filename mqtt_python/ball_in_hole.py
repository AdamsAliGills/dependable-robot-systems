



import os
import matplotlib.pyplot as plt
import sys
import imutils 
import glob
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time


    

def ball_tracking(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to load image from {image_path}")
        return None, None, None  # fix: return 3 values

    frame = imutils.resize(image, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    orange_lower = np.array([1, 100, 150])
    orange_upper = np.array([25, 255, 255])
  
    
    mask = cv2.inRange(hsv, orange_lower, orange_upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    radius = 0
    
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        if radius > 10:
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
    else:
        print(f"No ball detected in {os.path.basename(image_path)}")

    cv2.imshow("Ball Tracking", frame)
    cv2.imshow("Mask", mask)
    
    print(f"Image: {os.path.basename(image_path)} | Center: {center} | Radius: {radius:.1f}px")
    
    key = cv2.waitKey(0) & 0xFF
    cv2.destroyAllWindows()
    
    return center, radius, key  # always 3 values

# --- run on a single image ---

def tune_hsv(image_path):
    """Helper to give a UI to tune HSV for simpler tuning"""
    image = cv2.imread(image_path)
    frame = imutils.resize(image, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    def nothing(x):
        pass

    cv2.namedWindow("Trackbars")
    cv2.createTrackbar("H low",  "Trackbars", 1,  179, nothing)
    cv2.createTrackbar("H high", "Trackbars", 30, 179, nothing)
    cv2.createTrackbar("S low",  "Trackbars", 80, 255, nothing)
    cv2.createTrackbar("S high", "Trackbars", 255, 255, nothing)
    cv2.createTrackbar("V low",  "Trackbars", 80, 255, nothing)
    cv2.createTrackbar("V high", "Trackbars", 255, 255, nothing)

    print("Adjust trackbars to tune HSV. Press Q when happy with the values.")

    while True:
        h_low  = cv2.getTrackbarPos("H low",  "Trackbars")
        h_high = cv2.getTrackbarPos("H high", "Trackbars")
        s_low  = cv2.getTrackbarPos("S low",  "Trackbars")
        s_high = cv2.getTrackbarPos("S high", "Trackbars")
        v_low  = cv2.getTrackbarPos("V low",  "Trackbars")
        v_high = cv2.getTrackbarPos("V high", "Trackbars")

        lower = np.array([h_low,  s_low,  v_low])
        upper = np.array([h_high, s_high, v_high])

        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.erode(mask,  None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # overlay mask on frame so you can see what's being detected
        result = cv2.bitwise_and(frame, frame, mask=mask)

        cv2.imshow("Mask",   mask)
        cv2.imshow("Result", result)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            print(f"Final HSV range:")
            print(f"  orange_lower = np.array([{h_low}, {s_low}, {v_low}])")
            print(f"  orange_upper = np.array([{h_high}, {s_high}, {v_high}])")
            break

    cv2.destroyAllWindows()



if __name__ == "__main__":
# tune_hsv("/home/kkristjansson/DTU/spring2026/34755_dependableRobotSystems/images_new/golf_ball/image_2026_Feb_25_174725_009.jpg")

#TODO: Need to adjust HSV interval based on these 3 images also
# "image_2026_Feb_25_174723_007.jpg"
#  orange_lower = np.array([0, 64, 2])
#   orange_upper = np.array([33, 255, 255])

# "image_2026_Feb_25_174724_008.jpg
# orange_lower = np.array([0, 57, 5])
#   orange_upper = np.array([30, 255, 255])

# "# image_2026_Feb_25_174725_009.jpg
# orange_lower = np.array([0, 33, 38])
#   orange_upper = np.array([32, 255, 255])



    folder_path = "/home/kkristjansson/DTU/spring2026/34755_dependableRobotSystems/images_new/golf_ball"
 

    extensions = ["*.jpg", "*.jpeg", "*.png", "*.bmp"]
   
   
    image_paths = []
    for ext in extensions:
        image_paths.extend(glob.glob(os.path.join(folder_path, ext)))
    image_paths.sort()

    if len(image_paths) == 0:
        print(f"No images found in {folder_path}")
    else:
        print(f"Found {len(image_paths)} images. Press any key to advance, Q to quit.")
        for i, image_path in enumerate(image_paths):
            print(f"\n[{i+1}/{len(image_paths)}]")
            center, radius, key = ball_tracking(image_path)
            if key == ord("q"):  # press Q to quit early
                print("Quitting early")
                break

    cv2.destroyAllWindows()
    print("Done")


