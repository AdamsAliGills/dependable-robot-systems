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
import pytest

def main():
    pass


def calibrate_camera():
    pass
    

def ball_tracking(image_path):
    """Get's the outline of a golf ball as well as distinguishing between
        falsely detected golf balls """
    #Some constraints to limit detection of false golf balls
    MIN_Y = 160
    MIN_CIRC = 0.49
    MIN_RAD = 10
    MAX_RAD = 50

    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to load image from {image_path}")
        return None, None, None

    frame = imutils.resize(image, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # Necessary HSV thresholds for seperating orangeness from background
    orange_lower = np.array([1, 100, 150])
    orange_upper = np.array([25, 255, 255])

    mask = cv2.inRange(hsv, orange_lower, orange_upper)
    mask = cv2.erode(mask, None, iterations=3) #rid of noise
    mask = cv2.dilate(mask, None, iterations=4) #recover ball shape from eroding

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    center = None
    best_radius = 0
    candidates = []  # all circles that pass circularity check

    for c in cnts:
        area = cv2.contourArea(c)
        perimeter = cv2.arcLength(c, True)
        if perimeter == 0:
            continue

        circularity = (4 * np.pi * area) / (perimeter ** 2)
        ((x, y), radius) = cv2.minEnclosingCircle(c)

        if circularity > MIN_CIRC and MIN_RAD < radius < MAX_RAD and y > MIN_Y:
            candidates.append((c, x, y, radius, circularity))

    print(f"\nImage: {os.path.basename(image_path)} | {len(candidates)} candidate(s) found")

    if candidates:
        # Draw ALL candidates in green with their stats
        for i, (c, x, y, radius, circularity) in enumerate(candidates):
            cx, cy = int(x), int(y)
            r = int(radius)
            # green circle for all candidates
            cv2.circle(frame, (cx, cy), r, (0,255,0), 1)
            # Label: index, radius, circularity
            label = f"#{i} r={r} c={circularity:.2f}"
            label = f"#{i} r={r} circ={circularity:.2f} y={cy}"
            cv2.putText(frame, label, (cx - r, cy - r - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,255,0), 1)

        # Pick closest to camera a.k.a highest y-pixel value
        best = max(candidates, key=lambda item: item[2])
        best_c, best_x, best_y, best_radius, best_circ = best

        M = cv2.moments(best_c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # Draw winner in yellow, center dot in red
        cv2.circle(frame, (int(best_x), int(best_y)), int(best_radius), (0, 255, 255), 2)
        cv2.circle(frame, center, 5, (0, 0, 255), -1)

        # Winner label
        winner_label = f"BEST r={int(best_radius)} circ={best_circ:.2f} y={int(best_y)}"
        cv2.putText(frame, winner_label,
                    (int(best_x) - int(best_radius), int(best_y) - int(best_radius) - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        result_winner = (f"  Winner → center: {center}, radius: {best_radius:.1f}, circularity: {best_circ:.2f}")
        print(result_winner)
        for i, (_, x, y, r, circ) in enumerate(candidates):
            result = (f"  #{i} → pos: ({int(x)}, {int(y)}), radius: {r:.1f}, circularity: {circ:.2f}")
    else:
        result = (f"  No circular candidates found")
    print(result)
    with open("pattern_analysis_w_ball_test1.txt","a") as f:
        try:  
            f.write(f"{result}\n")
            f.write(f"{result_winner}\n")
            f.write()
        except:
            pass
    # cv2.imshow("Ball Tracking", frame)
    # cv2.imshow("Mask", mask)

    # key = cv2.waitKey(0) & 0xFF
    # cv2.destroyAllWindows()

    return center, best_radius

def erosion_values(img_original,mask,desired_value):
    """To try various erosion values for optimization of HSV mask"""
    mask1 = cv2.erode(mask, None, iterations=1) #removes noise
    mask2 = cv2.erode(mask, None, iterations=2) #removes noise
    mask3 = cv2.erode(mask, None, iterations=3) #removes noise
    mask4 = cv2.erode(mask, None, iterations=4) #removes noise
    mask5 = cv2.erode(mask, None, iterations=5) #removes noise
    mask6= cv2.erode(mask, None, iterations=6)
    mask7= cv2.erode(mask, None, iterations=7)
    mask8= cv2.erode(mask, None, iterations=8)
    mask9= cv2.erode(mask, None, iterations=9)
    mask10= cv2.erode(mask, None, iterations=10)

    # mask = cv2.dilate(mask, None, iterations=2)


    fig, ax = plt.subplots(nrows = 2, ncols = 6, figsize = (30,10))
    ax[0][0].imshow(mask1, cmap = 'gray')
    ax[0][0].set_title("erosion 1")

    ax[0][1].imshow(mask2, cmap = 'gray')
    ax[0][1].set_title("erosion 2")

    ax[0][2].imshow(mask3, cmap = 'gray')
    ax[0][2].set_title("erosion 3")

    ax[0][3].imshow(mask4, cmap = 'gray')
    ax[0][3].set_title("erosion 4")

    ax[0][4].imshow(mask5, cmap = 'gray')
    ax[0][4].set_title("erosion 5")

    ax[0][5].imshow(img_original)
    ax[1][0].imshow(mask6, cmap = 'gray')
    ax[1][0].set_title("erosion 6")

    ax[1][1].imshow(mask7, cmap = 'gray')
    ax[1][1].set_title("erosion 7")

    ax[1][2].imshow(mask8, cmap = 'gray')
    ax[1][2].set_title("erosion 8")

    ax[1][3].imshow(mask9, cmap = 'gray')
    ax[1][3].set_title("erosion 9")

    ax[1][4].imshow(mask10, cmap = 'gray')
    ax[1][4].set_title("erosion 10")

    plt.tight_layout()
    plt.show()

    mask = cv2.erode(mask,None,iterations = desired_value)
    return mask

def dilation_values(img_original,mask):
    mask1 = cv2.dilate(mask, None, iterations=1) #removes noise
    mask2 = cv2.dilate(mask, None, iterations=2) #removes noise
    mask3 = cv2.dilate(mask, None, iterations=3) #removes noise
    mask4 = cv2.dilate(mask, None, iterations=4) #removes noise
    mask5 = cv2.dilate(mask, None, iterations=5) #removes noise
    mask6= cv2.dilate(mask, None, iterations=6)
    mask7= cv2.dilate(mask, None, iterations=7)
    mask8= cv2.dilate(mask, None, iterations=8)
    mask9= cv2.dilate(mask, None, iterations=9)
    mask10= cv2.dilate(mask, None, iterations=10)

    # mask = cv2.dilate(mask, None, iterations=2)


    fig, ax = plt.subplots(nrows = 2, ncols = 6, figsize = (30,10))
    ax[0][0].imshow(mask1, cmap = 'gray')
    ax[0][0].set_title("dilation 1")

    ax[0][1].imshow(mask2, cmap = 'gray')
    ax[0][1].set_title("dilation 2")

    ax[0][2].imshow(mask3, cmap = 'gray')
    ax[0][2].set_title("dilation 3")

    ax[0][3].imshow(mask4, cmap = 'gray')
    ax[0][3].set_title("dilation 4")

    ax[0][4].imshow(mask5, cmap = 'gray')
    ax[0][4].set_title("dilation 5")

    ax[0][5].imshow(img_original)
    ax[1][0].imshow(mask6, cmap = 'gray')
    ax[1][0].set_title("dilation 6")

    ax[1][1].imshow(mask7, cmap = 'gray')
    ax[1][1].set_title("dilation 7")

    ax[1][2].imshow(mask8, cmap = 'gray')
    ax[1][2].set_title("dilation 8")

    ax[1][3].imshow(mask9, cmap = 'gray')
    ax[1][3].set_title("dilation 9")

    ax[1][4].imshow(mask10, cmap = 'gray')
    ax[1][4].set_title("dilation 10")

    plt.tight_layout()
    plt.show()

def test_outliers(img,path,desired_erosion):
    image_path = path+img
    image = cv2.imread(image_path)
    img_original = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

    frame = imutils.resize(image, width=600) #minimize frame size to increase FPS
    blurred = cv2.GaussianBlur(frame, (11, 11), 0) #decrease noise 
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV) #convert from bgr to hsv
    
    # Definition of orange HSV boundaries
    orange_lower = np.array([1, 100, 150]) 
    orange_upper = np.array([25, 255, 255])
  
    mask = cv2.inRange(hsv, orange_lower, orange_upper)
    mask = erosion_values(img_original,mask,desired_erosion)
    dilation_values(img_original,mask)

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

#TODO: 3 Trouble images
# "image_2026_Feb_25_174723_007.jpg"
#  orange_lower = np.array([0, 64, 2])
#   orange_upper = np.array([33, 255, 255])

# "image_2026_Feb_25_174724_008.jpg
# orange_lower = np.array([0, 57, 5])
#   orange_upper = np.array([30, 255, 255])

# "# image_2026_Feb_25_174725_009.jpg
# orange_lower = np.array([0, 33, 38])
#   orange_upper = np.array([32, 255, 255])

    
    folder_path = "/home/kkristjansson/DTU/spring2026/34755_dependableRobotSystems/images_new/golf_ball/"
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



            # img1 = "image_2026_Feb_25_174723_007.jpg"
            # img2 = "image_2026_Feb_25_174724_008.jpg"
            # img3 = "image_2026_Feb_25_174725_009.jpg"
            # test_outliers(img1,folder_path,4)
            # test_outliers(img2,folder_path,4)
            # test_outliers(img3,folder_path,4)


            center, radius = ball_tracking(image_path)
            # if key == ord("q"):  # press Q to quit early
            #     print("Quitting early")
            #     break

    cv2.destroyAllWindows()
    print("Done")


