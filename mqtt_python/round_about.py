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
    def __init__(self):
        '''Constructor for the roundAbout mission'''
        self.name = "RoundAbout"
        self.starting_tilt = abs(pose.pose[3]*180.0/3.14159) # store the original tilt in degrees
        self.state = 0
        self.target_angle = 180
        self.stable_count = 0
        print("-----------------------------------------")
        print("INITIALIZING ROUNDABOUT MISSION")
        print("-----------------------------------------")

    def logger(self):
        '''Logs the tilt to a loggings_.txt file for debugging'''
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
        while not service.stop:
            if self.state == 0:  # TODO: Synchronize this state with line following mission
                service.send("robobot/cmd/ti", "rc 0.2 0.0") #TODO: Remove this line
                self.state = 1 

            elif self.state == 1:
                current_tilt = abs(pose.pose[3]*180.0/3.14159)
                drop = self.starting_tilt - current_tilt
                print(f"Tilt: {current_tilt:.4f}  Drop: {drop:.4f}") 
                if drop > 3:  # Estimate threshold for detecting the drop into the roundabout, based on trial and error
                    self.state = 2
                    print(f"Detected drop of {drop:.4f} degrees. Current tilt: {current_tilt:.4f} degrees.")
               
            elif self.state == 2:  # slow down to climb
                print("-----------------------------------------")
                print(f"Detected roundabount, tilt @ {current_tilt:.4f}...")
                print("-----------------------------------------") 
                service.send("robobot/cmd/ti", "rc 0.05 0.0")
                self.state = 3

            elif self.state == 3:  # wait until fully on platform
                print(f"Current tilt: {abs(pose.pose[3]*180.0/3.14159)}, stable count: {self.stable_count}")
                current_tilt = abs(pose.pose[3] * 180.0 / 3.14159)
                if (self.stable_count >= 5 and # count based on trial and error. Can be adjusted. 
                current_tilt  <= 180 and # threshold based on measurements for tilt when fully on platform
                current_tilt >= 175): #threshold based on measurements for tilt when fully on platform
                    service.send("robobot/cmd/ti", "rc 0.0 0.0")
                    ("-----------------------------------------")
                    print(f"On roundabout, tilt @ {pose.pose[3]*180.0/3.14159}")
                    ("-----------------------------------------")
                    print("% RoundAbout: on platform, starting turn")
                    self.state = 11
                    
                if (self.get_delta_tilt() < 2 and  # 2 degrees delta for stability, based on trial and error
                    current_tilt >= 174 # threshold based on measurements for tilt when fully on platform
                    and current_tilt <= 177): #threshold based on measurements for tilt when fully on platform
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