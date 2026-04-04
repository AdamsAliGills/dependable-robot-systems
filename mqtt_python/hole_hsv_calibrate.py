from __future__ import print_function
import cv2
import argparse
import os
import tomllib
import tomli_w
from scam import cam
from uservice import service
from setproctitle import setproctitle


settings_file = "hsv_settings.toml"
max_value = 255
max_value_H = 180
low_H, low_S, low_V = 0, 0, 0
high_H, high_S, high_V = max_value_H, max_value, max_value

window_capture_name = "Video Capture"
window_detection_name = "Object Detection"
low_H_name, low_S_name, low_V_name = "Low H", "Low S", "Low V"
high_H_name, high_S_name, high_V_name = "High H", "High S", "High V"


def load_settings():
    global low_H, high_H, low_S, high_S, low_V, high_V
    if os.path.exists(settings_file):
        with open(settings_file, "rb") as f:
            data = tomllib.load(f)
            t = data.get("thresholds", {})
            low_H = t.get("low_H", 0)
            high_H = t.get("high_H", max_value_H)
            low_S = t.get("low_S", 0)
            high_S = t.get("high_S", max_value)
            low_V = t.get("low_V", 0)
            high_V = t.get("high_V", max_value)


def save_settings():
    data = {
        "thresholds": {
            "low_H": low_H,
            "high_H": high_H,
            "low_S": low_S,
            "high_S": high_S,
            "low_V": low_V,
            "high_V": high_V,
        }
    }
    with open(settings_file, "wb") as f:
        tomli_w.dump(data, f)


def on_low_H_thresh_trackbar(val):
    global low_H
    low_H = min(high_H - 1, val)
    cv2.setTrackbarPos(low_H_name, window_detection_name, low_H)


def on_high_H_thresh_trackbar(val):
    global high_H
    high_H = max(val, low_H + 1)
    cv2.setTrackbarPos(high_H_name, window_detection_name, high_H)


def on_low_S_thresh_trackbar(val):
    global low_S
    low_S = min(high_S - 1, val)
    cv2.setTrackbarPos(low_S_name, window_detection_name, low_S)


def on_high_S_thresh_trackbar(val):
    global high_S
    high_S = max(val, low_S + 1)
    cv2.setTrackbarPos(high_S_name, window_detection_name, high_S)


def on_low_V_thresh_trackbar(val):
    global low_V
    low_V = min(high_V - 1, val)
    cv2.setTrackbarPos(low_V_name, window_detection_name, low_V)


def on_high_V_thresh_trackbar(val):
    global high_V
    high_V = max(val, low_V + 1)
    cv2.setTrackbarPos(high_V_name, window_detection_name, high_V)


load_settings()
cv2.namedWindow(window_capture_name)
cv2.namedWindow(window_detection_name)

cv2.createTrackbar(
    low_H_name, window_detection_name, low_H, max_value_H, on_low_H_thresh_trackbar
)
cv2.createTrackbar(
    high_H_name, window_detection_name, high_H, max_value_H, on_high_H_thresh_trackbar
)
cv2.createTrackbar(
    low_S_name, window_detection_name, low_S, max_value, on_low_S_thresh_trackbar
)
cv2.createTrackbar(
    high_S_name, window_detection_name, high_S, max_value, on_high_S_thresh_trackbar
)
cv2.createTrackbar(
    low_V_name, window_detection_name, low_V, max_value, on_low_V_thresh_trackbar
)
cv2.createTrackbar(
    high_V_name, window_detection_name, high_V, max_value, on_high_V_thresh_trackbar
)


def loop():
    while not (service.stop):
        ok, frame, imgTime = cam.getImage()
        if frame is None:
            break

        frame_HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        frame_threshold = cv2.inRange(
            frame_HSV, (low_H, low_S, low_V), (high_H, high_S, high_V)
        )

        # UI Text Overlay
        cv2.putText(
            frame_threshold,
            f"H: {low_H}-{high_H}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame_threshold,
            f"S: {low_S}-{high_S}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame_threshold,
            f"V: {low_V}-{high_V}",
            (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame_threshold,
            "S: Save | Q: Quit",
            (10, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (150, 150, 150),
            1,
        )

        cv2.imshow(window_capture_name, frame)
        cv2.imshow(window_detection_name, frame_threshold)

        key = cv2.waitKey(30)
        if key == ord("q") or key == 27:
            break
        elif key == ord("s"):
            save_settings()

    cv2.destroyAllWindows()


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
