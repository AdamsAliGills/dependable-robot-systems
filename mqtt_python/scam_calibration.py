# scamera_utils.py
import numpy as np
import cv2

class CameraCalib:
    def __init__(self):
        '''Get required calibration files'''
        try:
            self.mtx  = np.loadtxt("calib_mtx.txt")
        except FileNotFoundError:
            print("No matrix calibrartion file found")
        # Load dist if available, otherwise assume zero distortion
        try:
            self.dist = np.loadtxt("calib_dist.txt")
        except FileNotFoundError:
            print("% No calib_dist.txt found, assuming zero distortion")
            self.dist = np.zeros((1, 5))

        self.fx = self.mtx[0, 0]
        self.fy = self.mtx[1, 1]
        self.cx = self.mtx[0, 2]
        self.cy = self.mtx[1, 2]

    def undistort(self, frame):
        """Undistort a raw camera frame before processing."""
        return cv2.undistort(frame, self.mtx, self.dist)

    def pixel_to_angle(self, cx_pixel, cy_pixel):
        """Convert a pixel center to horizontal and vertical angle in radians.
        Useful for steering toward the ball."""
        angle_x = np.arctan2(cx_pixel - self.cx, self.fx)  # left/right
        angle_y = np.arctan2(cy_pixel - self.cy, self.fy)  # up/down
        return angle_x, angle_y

    def estimate_distance(self, radius_pixels, real_diameter_m=0.0427):
        """Estimate distance to golf ball from its apparent radius.
        Golf ball diameter = 42.7mm"""
        if radius_pixels <= 0:
            return None
        # distance = (focal_length * real_radius) / pixel_radius
        real_radius_m = real_diameter_m / 2
        distance = (self.fx * real_radius_m) / radius_pixels
        return distance

