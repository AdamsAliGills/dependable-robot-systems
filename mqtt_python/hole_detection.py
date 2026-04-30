import cv2
import sys
import numpy as np
from scam import cam
from uservice import service
from setproctitle import setproctitle
import imutils

"""
hole detector draft script, with various params to tune
so that we can detect the exact hole in asta. 
"""


def hole_tacking(frame_rasp, display=True):
    MIN_Y = 50
    MIN_CIRC = 0.1
    MIN_AREA = 150

    low_H, low_S, low_V = 0, 85, 40
    high_H, high_S, high_V = 35, 200, 200

    frame = imutils.resize(frame_rasp, width=600)
    blurred = cv2.GaussianBlur(frame, (7, 7), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, (low_H, low_S, low_V), (high_H, high_S, high_V))

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    center = None
    best_area = 0
    candidates = []

    for c in cnts:
        area = cv2.contourArea(c)
        perimeter = cv2.arcLength(c, True)

        if perimeter == 0 or area < MIN_AREA:
            continue

        circularity = (4 * np.pi * area) / (perimeter**2)
        M = cv2.moments(c)
        if M["m00"] == 0:
            continue

        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        if circularity > MIN_CIRC and cy > MIN_Y:
            candidates.append((c, cx, cy, area, circularity))

    if candidates:
        best = max(candidates, key=lambda item: item[2])
        best_c, best_x, best_y, best_area, best_circ = best
        center = (best_x, best_y)

        cv2.drawContours(frame, [best_c], -1, (0, 255, 255), 2)
        cv2.circle(frame, center, 5, (0, 0, 255), -1)

        label = f"HOLE area={int(best_area)} circ={best_circ:.2f}"
        cv2.putText(
            frame,
            label,
            (best_x - 50, best_y - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            2,
        )

        print(f"  Hole found at {center}, Area: {best_area}")
    else:
        print("  No hole candidates found")

    if display:
        cv2.imwrite("hole_tracking_debug.jpg", frame)
        cv2.imwrite("hole_mask_debug.jpg", mask)

    return center
