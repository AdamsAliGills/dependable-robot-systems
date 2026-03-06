from uservice import service
from spose import pose
from simu import imu
import time
import math


from sedge import edge
from sir import ir

def driveToLine():
  state = 0
  dist_to_line = 0;
  print("% Driving to line ---------------------- right ir start ---")
  service.send("robobot/cmd/T0", "leds 16 0 100 0") # green
  while not (service.stop):
    if state == 0: # forward towards line
      service.send("robobot/cmd/ti","rc 0.2 0.0") # (forward m/s, turn-rate rad/sec)
      state = 1
    elif state == 1:
      if edge.lineValidCnt > 4:
        # start follow line
        edge.lineControl(0.2, True)
        service.send("robobot/cmd/T0","servo 1 0 0") # (move servo to position 0 - front)
    time.sleep(0.01)
  pass
  service.send("robobot/cmd/T0","leds 16 0 0 0") # end
  print("% Driving to line ------------------------- end")

class roundAbout():
    def __init__(self, target_angle: float):
        '''Constructor for the roundAbout mission'''
        self.name = "RoundAbout"
        self.starting_tilt = abs(pose.pose[3]*180.0/3.14159) # store the original tilt in degrees
        self.state = 0 #0 for kris's code, 11 for stefanos 
        self.target_angle = target_angle
        self.stable_count = 0
        print()
        print("creating roundAbout")
        print(f"Starting tilt: {self.starting_tilt:.4f} degrees")
        print()

    def print_current_tilt(self):
        '''Prints the current tilt of the robot in degrees'''
        t = 0
        while t < 30:
            if service.stop:
                break
            print(pose.pose[3]*180.0/3.14159)
            time.sleep(0.1)
            t += 0.1

    def get_delta_tilt(self):
        '''Gets the tilt delta over 0.3 seconds and returns it in degrees'''
        tilt_old = abs(pose.pose[3]*180.0/3.14159)
        time.sleep(0.2)
        tilt_new = abs(pose.pose[3]*180.0/3.14159)
        delta_tilt = abs(tilt_old - tilt_new)
        return delta_tilt

    def get_yaw(self):
        return imu.gyroIntegral[2]

    def execute(self):
        """Call this repeatedly from a loop - non-blocking state machine"""
        print("% RoundAbout: starting")
        while not service.stop:

            if self.state == 0:
                self.starting_tilt = abs(pose.pose[3]*180.0/3.14159)
                print("############################################################")
                print(f"Starting tilt at GND: {self.starting_tilt:.4f}")
                print("############################################################")
                service.send("robobot/cmd/ti", "rc 0.1 0.0")  # was 0.02
                self.state = 1
            elif self.state == 111:  # tilt logging mode
                # determine log file name (don't overwrite existing)
                log_path = "loggings.txt"
                counter = 1
                while True:
                    try:
                        open(log_path, "x").close()  # "x" mode fails if file already exists
                        break
                    except FileExistsError:
                        log_path = f"loggings_{counter}.txt"
                        counter += 1

                print(f"Logging tilt to {log_path} ...")
                with open(log_path, "w") as f:
                    while not service.stop:
                        tilt = abs(pose.pose[3] * 180.0 / 3.14159)
                        timestamp = time.strftime("%H:%M:%S")
                        line = f"{timestamp}, {tilt:.6f}\n"
                        f.write(line)
                        f.flush()
                        time.sleep(0.1)

            elif self.state == 1:
                current_tilt = abs(pose.pose[3]*180.0/3.14159)
                drop = self.starting_tilt - current_tilt
                print(f"Tilt: {current_tilt:.4f}  Drop: {drop:.4f}")  # add this temporarily to see whats happening
                if drop < -1:  # lowered from 1.0
                    self.state = 2
                    print(f"HIT RAMP, TILT: {current_tilt:.4f}")
            elif self.state == 2:  # slow down to climb
                service.send("robobot/cmd/ti", "rc 0.1 0.0")
                self.state = 3

            elif self.state == 3:  # wait until fully on platform
                current_tilt = abs(pose.pose[3] * 180.0 / 3.14159)
                if (self.stable_count >= 5 and 
                current_tilt  <= 180 and
                current_tilt >= 176):
                    service.send("robobot/cmd/ti", "rc 0.0 0.0")
                    print("############################################################")
                    print(f"ON ROUNDABOUT, TILT: {current_tilt:.4f}")
                    print("############################################################")
                    self.state = 99
                    service.stop = True
                    
                if self.get_delta_tilt() < 2.0:
                    self.stable_count += 1
                else:
                    self.stable_count = 0 # Reset count if tilt changes significantly
                 





              

            elif self.state == 11:
                # start turning 90 degrees
                self.start_yaw = self.get_yaw()
                angular_speed = math.copysign(0.7, -self.target_angle)
                service.send("robobot/cmd/ti", f"rc 0.0 {angular_speed}")
                self.state = 12

            elif self.state == 12:
                # when 90 degrees are reached, start rotating
                print(abs(self.get_yaw() - self.start_yaw))
                if abs(self.get_yaw() - self.start_yaw) >= 80:  # 80 because it overshoots a bit
                    radius = 0.33  # radius of the roundabout in meters
                    speed = 0.2   # speed for the roundabout in meters/second
                    angular_speed = math.copysign(speed/radius, self.target_angle)
                    service.send("robobot/cmd/ti", f"rc {speed} {angular_speed}")
                    self.start_yaw = self.get_yaw()
                    self.state = 13

            elif self.state == 13:
                print(abs(self.get_yaw() - self.start_yaw))
                # when the target angle (minus 45 degrees) is reached, finish
                if abs(self.get_yaw() - self.start_yaw) >= abs(self.target_angle) - 75:
                    self.state = 99

            else:
                service.send("robobot/cmd/ti", "rc 0.0 0.0")
                print("% RoundAbout: complete")
                driveToLine()
                break

        print(f"% On roundabout, starting to turn.")