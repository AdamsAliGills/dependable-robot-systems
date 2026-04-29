import datetime
from datetime import datetime
import os
import matplotlib.pyplot as plt
import sys
import imutils 
import glob
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
# import pytest
from scam import cam
from sgpio import gpio
from matplotlib import image as io

#------------------------------
# Folder paths for test images
BLUE_BALL_FOLDER    = "/home/kkristjansson/DTU/spring2026/34755_dependableRobotSystems/images_weird_balls_local/images_weird_balls/blue_ball"
RED_BALL_FOLDER    = "/home/kkristjansson/DTU/spring2026/34755_dependableRobotSystems/images_weird_balls_local/images_weird_balls/red_ball"
WHITE_BALL_FOLDER    = "/home/kkristjansson/DTU/spring2026/34755_dependableRobotSystems/images_weird_balls_local/images_weird_balls/white_ball"
NO_BALL_FOLDER    = "/home/kkristjansson/DTU/spring2026/34755_dependableRobotSystems/images_weird_balls_local/images_weird_balls/no_ball"
ALL_BALLS_FOLDER    = "/home/kkristjansson/DTU/spring2026/34755_dependableRobotSystems/images_weird_balls_local/images_weird_balls/all_balls"




#------------------------------

#------------------------------
# Expected results for images with the ball in, based on pixel coordinates
EXPECTED_RESULTS = {
    "image_2026_Feb_25_174717_001.jpg": (458, 329),
    "image_2026_Feb_25_174718_002.jpg": (320, 213),
    "image_2026_Feb_25_174719_003.jpg": (221, 233),
    "image_2026_Feb_25_174720_004.jpg": (292, 268),
    "image_2026_Feb_25_174721_005.jpg": (268, 314),
    "image_2026_Feb_25_174722_006.jpg": (275, 397),
    "image_2026_Feb_25_174723_007.jpg": (582, 425),
    "image_2026_Feb_25_174724_008.jpg": (370, 291),
    "image_2026_Feb_25_174725_009.jpg": (172, 288),
    "image_2026_Feb_25_174726_010.jpg": (325, 378),
    "image_2026_Feb_25_174727_011.jpg": (280, 313),
    "image_2026_Feb_25_174728_012.jpg": (390, 376),
    "image_2026_Feb_25_174729_013.jpg": (375, 437),
    "image_2026_Feb_25_174730_014.jpg": (299, 353),
}
 
CENTER_TOLERANCE = 5  # wiggle-room



def get_image():
    if cam.useCam:
        ok, img, imgTime = cam.getImage()
    cv2.namedWindow("Input")
    cv2.imshow("image",img)
    cv2.waitKey(0)
    
def check_if_in_exclusion_zone(x, y):
    EXCLUSION_ZONES = [
        (0,   274, 147, 176),
    (487, 268, 112, 181),
    ]
    for (zx,zy,zw,zh) in EXCLUSION_ZONES:
        if zx <= x <= zx+zw and zy <= y <= zy+zh:
            return True
    return False

def ball_tracking(frame_rasp,display = False, ball_color = type(str)):
    """Get's the outline of a golf ball as well as distinguishing between
        falsely detected golf balls """
    #Some constraints to limit detection of false golf balls
    if ball_color == "orange":
        MIN_Y = 160
        MIN_CIRC = 0.49
        MIN_RAD = 10
        MAX_RAD = 50
    else:
        MIN_Y = 100
        MIN_CIRC = 0.50
        MIN_RAD = 10
        MAX_RAD = 60



    frame = imutils.resize(frame_rasp, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # Necessary HSV thresholds for seperating orangeness from background
    if ball_color == "orange":
        lower_hsv = np.array([1, 100, 150])
        upper_hsv = np.array([25, 255, 255])
    elif ball_color == "red":
        lower_hsv = np.array([120, 71, 138])
        upper_hsv = np.array([179, 255, 255])

        lower_hsv = np.array([0, 126, 69])
        upper_hsv = np.array([17, 255, 255])


    elif ball_color == "blue":
        lower_hsv = np.array([89, 33, 64])
        upper_hsv = np.array([112, 250, 255])

        lower_hsv = np.array([92, 60, 64])
        upper_hsv = np.array([134, 255, 255])
    else:
        pass

    if ball_color in ["orange", "red", "blue"]:
        mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
        mask = cv2.erode(mask, None, iterations=3) #rid of noise

    else:
        mask = cv2.erode(frame, None, iterations=3) #rid of noise

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

    # print(f"\nImage: {os.path.basename(image_path)} | {len(candidates)} candidate(s) found")

    result_log = []
    result_winner_log = None
    candidates = [
        (c, x, y, radius, circularity)
        for (c, x, y, radius, circularity) in candidates
        if not check_if_in_exclusion_zone(x, y)
    ]
    if candidates:
        for i, (c, x, y, radius, circularity) in enumerate(candidates):
            cx, cy = int(x), int(y)
            r      = int(radius)
            cv2.circle(frame, (cx, cy), r, (0, 255, 0), 1)
            label = f"#{i} r={r} circ={circularity:.2f} y={cy}"
            cv2.putText(frame, label, (cx - r, cy - r - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
            result_log.append(
                f"  #{i} → pos: ({int(x)}, {int(y)}), radius: {radius:.1f}, circularity: {circularity:.2f}"
            )
 
        # Pick closest to camera = highest y pixel value
        best = max(candidates, key=lambda item: item[2])
        best_c, best_x, best_y, best_radius, best_circ = best
 
        M = cv2.moments(best_c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
 
        cv2.circle(frame, (int(best_x), int(best_y)), int(best_radius), (0, 255, 255), 2)
        cv2.circle(frame, center, 5, (0, 0, 255), -1)
 
        winner_label = f"BEST r={int(best_radius)} circ={best_circ:.2f} y={int(best_y)}"
        cv2.putText(frame, winner_label,
                    (int(best_x) - int(best_radius), int(best_y) - int(best_radius) - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
 
        result_winner_log = (
            f"  Winner → center: {center}, radius: {best_radius:.1f}, circularity: {best_circ:.2f}"
        )
        print(result_winner_log)
    else:
        print("  No circular candidates found")
 
    for line in result_log:
        print(line)
    
    
    # if display:
    #     with open("pattern_analysis_w_ball_test1.txt", "a") as f:
    #         for line in result_log:
    #             f.write(line + "\n")
    #         if result_winner_log:
    #             f.write(result_winner_log + "\n")
    
    target_x, target_y, target_r = 284, 357, 44
    cv2.circle(frame, (target_x, target_y), target_r, (255, 0, 0), 2)        # outer circle
    cv2.line(frame, (target_x - target_r, target_y), (target_x + target_r, target_y), (255, 0, 0), 1)  # horizontal
    cv2.line(frame, (target_x, target_y - target_r), (target_x, target_y + target_r), (255, 0, 0), 1)  # vertical
    cv2.circle(frame, (target_x, target_y), 3, (255, 0, 0), -1)              # center dot

    saved_time = time.time()
    dt_object = datetime.fromtimestamp(saved_time)
    formatted_time = dt_object.strftime("%Y-%m-%d_%H-%M-%S-%f")

    cv2.imwrite(f"ball_tracking_frame_{ball_color}_{formatted_time}.jpg", frame)
    cv2.imwrite(f"ball_tracking_mask_{ball_color}_{formatted_time}.jpg", mask)
    print(f"% Saved ball_tracking_frame_{ball_color}_{formatted_time}.jpg and ball_tracking_mask_{ball_color}_{formatted_time}.jpg")
    

    return center, best_radius

def _get_images_from_folder(folder): 
    """Get images from folder for pytests"""
    paths = []
    for ext in ["*.jpg", "*.jpeg", "*.png", "*.bmp"]:
        paths.extend(glob.glob(os.path.join(folder, ext)))
    return sorted(paths)


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

def find_first_ball(img):
    img = cv2.imread(img)
    
    prevCircle = None
    dist = lambda x1,y1,x2,y2: ((x1-x2)**2 + (y1-y2)**2)
    
    grayFrame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(grayFrame, 230, 255, cv2.THRESH_BINARY)    
    cv2.imshow("Thresholded", thresh)
    blurFrame = cv2.GaussianBlur(thresh, (11,11), 2)

    circles = cv2.HoughCircles(blurFrame, cv2.HOUGH_GRADIENT, 1.2, minDist=10, param1=30, param2=15, minRadius=10, maxRadius=80) 
    #param1 the higher the threshold the higher standard of whether its a circle
    #param2 the amount of edge points that are needed to be considered a circle

    
    if circles is not None:
        circles = np.uint16(np.around(circles))  
        chosen = None
        for i in circles[0, :]:
            if chosen is None: chosen = i
            if prevCircle is not None:
                if dist(chosen[0],chosen[1],prevCircle[0],prevCircle[1]) < dist(i[0],i[1],prevCircle[0],prevCircle[1]):
                    chosen = i
        cv2.circle(img, (chosen[0], chosen[1]), 1, (0, 100, 100), 3)
        cv2.circle(img, (chosen[0], chosen[1]), chosen[2], (255, 0, 255), 3)
        prevCircle = chosen
    else:
        print("No circles found")
    cv2.imshow("Found Circles", img)
    if cv2.waitKey(0) & 0xFF == ord('q'):
        cv2.destroyAllWindows()

if __name__ == "__main__":
    choice =  input("Enter whether to process many or single (m/s): ")
    if choice == "m":
        LENGTH_ALL_BALLS_FILES = 67
        LENGTH_BLUE_BALLS = 7
        LENGTH_RED_BALLS = 6
        for i in range(LENGTH_ALL_BALLS_FILES):
            img = ALL_BALLS_FOLDER + f"/frame_{i+1:05d}.jpg"
            # tune_hsv(img)
            # find_first_ball(img)
            try:
                ball_tracking(cv2.imread(img), display=True, ball_color="blue")
                ball_tracking(cv2.imread(img), display=True, ball_color="red")
            except AttributeError:
                pass
    else:
        img = RED_BALL_FOLDER + "/newest_1.jpg"
        ball_tracking(cv2.imread(img), display=True, ball_color="blue")

        # tune_hsv(img)