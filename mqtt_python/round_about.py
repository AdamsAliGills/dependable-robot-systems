from uservice import service
from spose import pose
from sedge import edge
from simu import imu
from random import choice
import time
import math


def get_tilt():
    return imu.gyroIntegral[1]

def get_yaw():
    return imu.gyroIntegral[2]

class roundAbout():
    def __init__(self, target_angle: float):
        '''Constructor for the roundAbout mission'''
        self.name = "RoundAbout"
        self.state = 0
        self.target_angle = target_angle
        print("-----------------------------------------")
        print("     INITIALIZING ROUNDABOUT MISSION     ")
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

    def execute(self):
        """Call this while following the line - blocking state machine"""
        print("% RoundAbout: starting")
        while not service.stop:

            if self.state == 0:
                edge.lineControl(0)
                self.starting_tilt = get_tilt() # store the original tilt in degrees
                service.send("robobot/cmd/T0", "servo 2 400 150")
                service.send("robobot/cmd/ti", f"rc 0.05 0.0")
                self.state = 1

            elif self.state == 1:
                current_tilt = get_tilt()
                print(f"tilt: {current_tilt}")
                if current_tilt < self.starting_tilt - 3:
                    self.timer = time.time()
                    self.state = 2
            elif self.state == 2:
                if time.time() - self.timer > 0.7:
                    edge.lineControl(0)
                    service.send("robobot/cmd/ti", f"rc 0.2 0.0")
                    self.state = 3

            elif self.state == 3:  # slow down to climb
                current_tilt = get_tilt()
                print(f"{current_tilt} > {self.starting_tilt - 1} ???")
                if current_tilt > self.starting_tilt - 1:
                    print(f"{current_tilt} > {self.starting_tilt - 1} !!!!")
                    service.send("robobot/cmd/ti", f"rc 0.0 0.0")
                    self.state = 11

            elif self.state == 11:
                # start turning 90 degrees
                self.start_yaw = get_yaw()
                angular_speed = math.copysign(0.7, -self.target_angle)
                service.send("robobot/cmd/ti", f"rc -0.02 {angular_speed}")
                self.state = 12

            elif self.state == 12:
                # when 90 degrees are reached, start rotating
                if abs(get_yaw() - self.start_yaw) >= 80:  # 80 because it overshoots a bit
                    radius = 0.33  # radius of the roundabout in meters
                    speed = 0.2   # speed for the roundabout in meters/second
                    angular_speed = math.copysign(speed/radius, self.target_angle)
                    service.send("robobot/cmd/ti", f"rc {speed} {angular_speed}")
                    self.start_yaw = get_yaw()
                    self.state = 13

            elif self.state == 13:
                # when the target angle (minus 45 degrees) is reached, exit going straight
                if abs(get_yaw() - self.start_yaw) >= abs(self.target_angle) - 75:
                    self.state = 14
                    service.send("robobot/cmd/ti","rc 0.2 0.0")

            elif self.state == 14:
                # when the line is found, finish
                if edge.lineValidCnt > 4:
                    service.send("robobot/cmd/T0", "servo 2 -200 150")
                    #service.send("robobot/cmd/ti","rc 0.0 0.0")
                    self.state = 99

            else:
                print("% RoundAbout: complete")
                return True

            time.sleep(0.05)
        return False


    def test(max_attempts: int, current_entrance = 45):
        entrance_list = [0, 45, 180, 270]

        for i in range(max_attempts):
            print(f"Round about test {i} starting")

            valid_entrances = [ e for e in entrance_list if abs(e - current_entrance) >= 75 or e == current_entrance ]
            new_entrance = choice(valid_entrances) # random exit
            angle = new_entrance - current_entrance
            angle = choice([angle, angle - 360]) # random direction
            angle = ((angle + 360) % 720) - 360 or 360

            print(f"new entrance: {new_entrance}")
            print(f"angle: {angle}")

            current_entrance = new_entrance

            r = roundAbout(angle)

            edge.lineControl(0.2)
            success = r.execute()
            if success:
                print(f"Round about test {i} successful")
            else:
                print(f"Round about test {i} gone wrong")
                return i


            edge.lineControl(0.2)

            # Wait 2 seconds non-blocking, return False if stopped
            wait_start = time.time()
            while time.time() - wait_start < 2:
                if service.stop:
                    return i
                time.sleep(0.01)
            edge.lineControl(0)

            start_yaw = get_yaw()
            service.send("robobot/cmd/ti", f"rc 0.0 1.0")

            while abs(get_yaw() - start_yaw) < 170:
                if service.stop:
                    return i
                time.sleep(0.01)
            service.send("robobot/cmd/ti", f"rc 0.0 0.0")

        return max_attempts