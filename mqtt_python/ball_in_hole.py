


#TODO: ADD CALIBRATION DATA VIA CHESS BOARD
# 1. Get orange 
    # a. get color range from image (use color picker)
    # b. convert image to hsv 
  
# 2. Get circle shape

import os
from skimage import color, io, measure, img_as_ubyte
from skimage.measure import profile_line
from skimage.transform import rescale, resize
import matplotlib.pyplot as plt
import numpy as np
import pydicom as dicom
import sys
import cv2 as cv
# class ballInHole():
#     def __init__(self, hole_diameter = float): #hole_diameter in mm
#         self.hole_diameter = hole_diameter
#         self.image_path_folder = "/home/kkristjansson/DTU/spring2026/34755_dependableRobotSystems/images_new"

#         print(f"Ball in hole mission initialized with hole diameter: {self.hole_diameter}")


    

    


if __name__ == "__main__":

   
    clear_image = io.imread("/home/kkristjansson/DTU/spring2026/34755_dependableRobotSystems/images_new/golf_ball/" \
    "image_2026_Feb_25_181532_003.jpg")


    clear_image_test = io.imread("/home/kkristjansson/DTU/spring2026/34755_dependableRobotSystems/images_new/golf_ball/" \
    "image_2026_Feb_25_181531_002.jpg")


    


    def ballinhole(image):

        clear_image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        hsv_image  = cv.cvtColor(clear_image, cv.COLOR_RGB2HSV)

        plt.figure(figsize=(6, 6))
        plt.imshow(hsv_image)
        plt.title("HSV image")
        plt.axis('off')
        plt.show()

        orange_lower = np.array([100,100 , 100])
        orange_upper = np.array([256, 256, 256])

        mask = cv.inRange(hsv_image, orange_lower, orange_upper)


        kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
        mask_clean = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)
        
        fig, axes = plt.subplots(1, 2, figsize=(30, 30))
        axes[0].imshow(mask, cmap='gray')
        axes[0].set_title("Mask - before cleanup")
        axes[0].axis('off')
        axes[1].imshow(mask_clean, cmap='gray')
        axes[1].set_title("Mask - after cleanup")
        axes[1].axis('off')
        plt.show()



        BALL_REAL_RADIUS_MM = 40.6  # standard golf ball radius, adjust if yours differs
        # Calibrate this once: measure pixel radius in an image at a known distance
        EXPECTED_PIXEL_RADIUS = 50   # tune this from your test images
        RADIUS_TOLERANCE = 20        # ± pixels allowed

        ball_candidates = []
        contours, _ = cv.findContours(mask_clean, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv.contourArea(cnt)
            if area < 100:  # just to skip tiny noise before heavier checks
                continue

            (cx, cy), radius = cv.minEnclosingCircle(cnt)

            if abs(radius - EXPECTED_PIXEL_RADIUS) > RADIUS_TOLERANCE:
                continue

            ball_candidates.append((cnt, (int(cx), int(cy)), int(radius)))

        ball_candinates = sorted(ball_candinates)
        ball_candinates = ball_candinates[-1]

        result_image = clear_image.copy()
        for cnt, (cx, cy), radius in ball_candidates:
            cv.circle(result_image, (cx, cy), radius, (0, 255, 0), 2)  # detected circle
            cv.circle(result_image, (cx, cy), 5, (255, 0, 0), -1)      # centroid dot
            print(f"Ball at ({cx}, {cy}) | Detected radius: {radius}px")  

            print(f"Centroid: ({int(cx)}, {int(cy)}) | Radius: {radius:.1f} | Circularity: {circularity:.2f} | Fill ratio: {fill_ratio:.2f}")

        plt.figure(figsize=(6, 6))
        plt.imshow(result_image)
        plt.title(f"Ball candidates found: {len(ball_candidates)}")
        plt.axis('off')
        plt.show()

    # ballInHole(40.6)  # Example hole diameter

    test_1 = ballinhole(clear_image)
    test_2 = ballinhole(clear_image_test)
