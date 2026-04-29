import cv2
import sys
import numpy as np
from scam import cam
from uservice import service
from setproctitle import setproctitle
import imutils

"""
QR / ArUco marker detector for markers labeled C and B.
"""

MARKER_IDS = {
    "C": [15],
    "B": [12],
}


def get_marker_angle(pts):
    """ Get the orientation of the arco marker in degrees"""
    top_left  = pts[0]
    top_right = pts[1]
    
    dx = top_right[0] - top_left[0]
    dy = top_right[1] - top_left[1]
    
    angle = np.degrees(np.arctan2(dy, dx))
    return angle

def qr_tacking(frame_rasp, marker_type, display=True):
    """
    Detect a specific marker ('C' or 'B') and return its center.

    Args:
        frame_rasp: Input BGR frame.
        marker_type: 'C' or 'B'.
        display: Save debug images if True.

    Returns:
        center: (x, y) tuple of marker center, or None.
    """
    MIN_AREA = 400

    frame = imutils.resize(frame_rasp, width=600)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    center = None
    candidates = []

    # Detect ArUco markers
    try:
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        parameters = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
        corners, ids, rejected = detector.detectMarkers(gray)
    except AttributeError:
        try:
            aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
            parameters = cv2.aruco.DetectorParameters_create()
            corners, ids, _ = cv2.aruco.detectMarkers(
                gray, aruco_dict, parameters=parameters
            )
        except Exception as e:
            print(f"ArUco detection not available: {e}")
            corners, ids = None, None

    if ids is not None:
        for i, marker_id in enumerate(ids.flatten()):
            pts = corners[i].reshape(4, 2)
            area = cv2.contourArea(pts)

            if area < MIN_AREA:
                continue

            cx = int(np.mean(pts[:, 0]))
            cy = int(np.mean(pts[:, 1]))

            # If mapping is empty, print ID for calibration
            if not MARKER_IDS.get(marker_type, []):
                print(f"    Detected marker ID {marker_id} at ({cx}, {cy})")
                candidates.append((pts, cx, cy, area, marker_id))
            elif marker_id in MARKER_IDS.get(marker_type, []):
                candidates.append((pts, cx, cy, area, marker_id))

    if candidates:
        best = max(candidates, key=lambda item: item[3])
        best_pts, best_x, best_y, best_area, best_id = best
        angle = get_marker_angle(best_pts.reshape(4, 2))
        center = (best_x, best_y)

        cv2.polylines(
            frame, [best_pts.astype(int).reshape(-1, 1, 2)], True, (0, 255, 255), 2
        )
        cv2.circle(frame, center, 5, (0, 0, 255), -1)

        label = f"{marker_type} id={best_id} area={int(best_area)}"
        cv2.putText(
            frame,
            label,
            (best_x - 50, best_y - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            2,
        )

        print(
            f"  {marker_type} marker found at {center}, ID: {best_id}, Area: {best_area}"
        )
    else:
        print(f"  No {marker_type} marker candidates found")

    if display:
        cv2.imwrite("qr_tracking_debug.jpg", frame)
        debug = frame.copy()
        if ids is not None:
            for i, marker_id in enumerate(ids.flatten()):
                pts = corners[i].reshape(4, 2).astype(int)
                c_x = int(np.mean(pts[:, 0]))
                c_y = int(np.mean(pts[:, 1]))
                cv2.polylines(debug, [pts.reshape(-1, 1, 2)], True, (255, 0, 0), 1)
                cv2.putText(
                    debug,
                    f"id:{marker_id}",
                    (c_x, c_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (255, 0, 0),
                    1,
                )
        cv2.imwrite("qr_all_debug.jpg", debug)

    return center,angle 
