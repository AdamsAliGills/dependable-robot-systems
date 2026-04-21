import time
from simu import imu
from sedge import edge
from uservice import service
from sir import ir

def wait_ramp_top(ramp_tilt: float, tolerance: float = 2.0, stable_time: float = 0.5):
    """
    Block until the robot reaches the top of a ramp of `ramp_tilt` degrees. (both going up or down)
    """
    stable_start = None
    start_tilt = imu.gyroIntegral[1] # tilt in degrees
    while not service.stop:
        current_tilt = imu.gyroIntegral[1] - start_tilt
        print(f"current tilt top: {current_tilt}")
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
        print(f"current tilt bottom: {current_tilt}")
        if -ramp_tilt - current_tilt >= -tolerance:
            if stable_start is None:
                stable_start = time.time()
            elif time.time() - stable_start >= stable_time:
                return  # ramp detected
        else:
            stable_start = None
        time.sleep(0.05)


def wait_turn(turn_angle: float):
    """
    Block until the robot reaches the top of a ramp of `ramp_tilt` degrees. (both going up or down)
    """
    start_yaw = imu.gyroIntegral[2] # yaw in degrees
    while not service.stop:
        current_yaw = imu.gyroIntegral[2] - start_yaw
        print(f"current yaw: {current_yaw}")
        if abs(current_yaw) >= abs(turn_angle):
            return
        time.sleep(0.05)

def wait_end():
    while not service.stop:
        if ir.ir[1] < 0.14:
            return
        time.sleep(0.01)

def wait_line():
    while not service.stop:
        if edge.lineValidCnt > 4:
            return
        time.sleep(0.01)
        
