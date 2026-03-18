import time
from simu import imu
from uservice import service

def wait_ramp_top(ramp_tilt: float, tolerance: float = 2.0, stable_time: float = 0.5):
    """
    Block until the robot reaches the top of a ramp of `ramp_tilt` degrees. (both going up or down)
    """
    stable_start = None
    start_tilt = imu.gyroIntegral[1] # tilt in degrees
    while not service.stop:
        current_tilt = imu.gyroIntegral[1] - start_tilt
        if ramp_tilt - current_tilt <= tolerance:
            if stable_start is None:
                stable_start = time.time()
            elif time.time() - stable_start >= stable_time:
                return  # ramp detected
        else:
            stable_start = None
        time.sleep(0.05)

def wait_ramp_bottom(ramp_tilt: float, tolerance: float = 2.0, stable_time: float = 0.5):
    """
    Block until the robot reaches the top of a ramp of `ramp_tilt` degrees. (both going up or down)
    """
    stable_start = None
    start_tilt = imu.gyroIntegral[1] # tilt in degrees
    while not service.stop:
        current_tilt = imu.gyroIntegral[1] - start_tilt
        if -ramp_tilt - current_tilt >= -tolerance:
            if stable_start is None:
                stable_start = time.time()
            elif time.time() - stable_start >= stable_time:
                return  # ramp detected
        else:
            stable_start = None
        time.sleep(0.05)
