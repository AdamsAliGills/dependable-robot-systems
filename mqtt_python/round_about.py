from uservice import service
from spose import pose
from sedge import edge
from simu import imu
import time
import math


class roundAbout():
    def __init__(self, target_angle: float):
        '''Constructor for the roundAbout mission'''
        self.name = "RoundAbout"
        self.state = 0
        self.target_angle = target_angle
        self.stable_count = 0
        print("-----------------------------------------")
        print("INITIALIZING ROUNDABOUT MISSION")
        print("-----------------------------------------")

    def setup_logger(self):
        '''Logs the tilt to a loggings_.txt file for debugging'''
                # determine log file name (don't overwrite existing)
        log_path = "loggings_IMU.txt"
        counter = 1
        while True:
            try:
                open(log_path, "x").close()  # "x" mode fails if file already exists
                break
            except FileExistsError:
                log_path = f"loggings_IMU{counter}.txt"
                counter += 1

        self.f = open(log_path, "w")

    def get_delta_tilt(self):
        '''Gets the tilt and returns it in degrees'''
        tilt_old = pose.pose[3]*180.0/3.14159 #radians to degrees
        time.sleep(0.2)
        tilt_new = pose.pose[3]*180.0/3.14159 #radians to degrees
        delta_tilt = abs(tilt_new - tilt_old)
        return delta_tilt

    def get_yaw(self):
        return imu.gyroIntegral[2]

    def execute(self):
        """Call this repeatedly from a loop - non-blocking state machine"""
        print("% RoundAbout: starting")
        self.setup_logger()
        while not service.stop:

            imu_tilt = imu.gyroIntegral[1]
            timestamp = time.strftime(f"{time.time() % 60}")
            line = f"{timestamp}, {imu_tilt:.6f}\n"
            self.f.write(line)
            self.f.flush()

            time.sleep(0.1)
            if self.state == 0:  # TODO: Synchronize this state with line following mission
                edge.lineControl(0.2)
                self.starting_tilt = imu.gyroIntegral[1] # store the original tilt in degrees
                self.state = 1

            elif self.state == 1:
                current_tilt = imu.gyroIntegral[1]
                if current_tilt < self.starting_tilt - 3:
                    self.state = 2
            elif self.state == 2:  # slow down to climb
                current_tilt = imu.gyroIntegral[1]
                if current_tilt > self.starting_tilt - 2:
                    edge.lineControl(0)
                    self.state = 11

            elif self.state == 11:
                # start turning 90 degrees
                self.start_yaw = self.get_yaw()
                angular_speed = math.copysign(0.7, -self.target_angle)
                service.send("robobot/cmd/ti", f"rc 0.0 {angular_speed}")
                self.state = 12

            elif self.state == 12:
                # when 90 degrees are reached, start rotating
                if abs(self.get_yaw() - self.start_yaw) >= 80:  # 80 because it overshoots a bit
                    radius = 0.33  # radius of the roundabout in meters
                    speed = 0.2   # speed for the roundabout in meters/second
                    angular_speed = math.copysign(speed/radius, self.target_angle)
                    service.send("robobot/cmd/ti", f"rc {speed} {angular_speed}")
                    self.start_yaw = self.get_yaw()
                    self.state = 13

            elif self.state == 13:
                # when the target angle (minus 45 degrees) is reached, exit going straight
                if abs(self.get_yaw() - self.start_yaw) >= abs(self.target_angle) - 75:
                    self.state = 14
                    service.send("robobot/cmd/ti","rc 0.2 0.0")

            elif self.state == 14:
                # when the line is found, start following it
                if edge.lineValidCnt > 4:
                    edge.lineControl(0.2, True) # start follow line
                    self.state = 99

            else:
                print("% RoundAbout: complete")
                break

            time.sleep(0.05)
