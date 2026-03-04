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
        self.starting_tilt = pose.pose[3]*180.0/3.14159 # store the original tilt in degrees
        self.state = 0 #0 for kris's code, 11 for stefanos 
        self.target_angle = target_angle
        print()
        print("creating roundAbout")
        print()
        

    def print_current_tilt(self):
        '''Prints the current tilt of the robot in degrees'''
        t = 0
        while t < 30:
            if service.stop:
                break
            print(pose.pose[3]*180.0/3.14159) # store the original tilt in degrees
            time.sleep(0.1)
            t += 0.1
            

    
        
    def get_delta_tilt(self):
        '''Gets the tilt and returns it in degrees'''
        tilt_old = pose.pose[3]*180.0/3.14159 #radians to degrees
        time.sleep(0.3)
        tilt_new = pose.pose[3]*180.0/3.14159 #radians to degrees
        delta_tilt = abs(tilt_new - tilt_old)
        return delta_tilt

    def get_yaw(self):
        return imu.gyroIntegral[2]

    def execute(self):
        """Call this repeatedly from a loop - non-blocking self.state machine"""
        print("% RoundAbout: starting")
        while not service.stop:
            if self.state == 0:  # approach until tilt detected
                print("############################################################")
                print(f"Starting tilt at GND: {pose.pose[3]*180.0/3.14159}")
                print("############################################################")
                service.send("robobot/cmd/ti", "rc 0.05 0.0")
                self.state = 1
            elif self.state == 1:  # wait until front wheel hits ramp
                if self.get_delta_tilt() > 2:
                    self.state = 2
                    print("############################################################")
                    print(f"HIT RAMP, TILT: {pose.pose[3]*180.0/3.14159}")
                    print("############################################################")
            elif self.state == 2:  # slow down to climb
                service.send("robobot/cmd/ti", "rc 0.1 0.0")
                self.state = 3

            elif self.state == 3:  # wait until fully on roundabout
                if abs(self.starting_tilt - (pose.pose[3]*180.0/3.14159)) < 3:
                    service.send("robobot/cmd/ti", "rc 0.0 0.0")
                    print("############################################################")
                    print(f"ON ROUNDABOUT, TILT: {pose.pose[3]*180.0/3.14159}")
                    print("############################################################")
                    print("% RoundAbout: on platform, starting turn")
                    self.state = 99
                    print("")
                    print("")
                    print("")
                    print("")
                    print("")
                    print("")
                    print("")
                    print("")
                    print("")
                    print("")

                    service.stop = True
                
                print(self.get_delta_tilt())
            
            elif self.state == 11:
                # start turning 90 degrees
                self.start_yaw = self.get_yaw()
                angular_speed = math.copysign(0.7, -self.target_angle)
                service.send("robobot/cmd/ti", f"rc 0.0 {angular_speed}")
                self.state = 12

            elif self.state == 12:
                # when 90 degrees are reached, start rotating
                print(abs(self.get_yaw() - self.start_yaw))
                if abs(self.get_yaw() - self.start_yaw) >= 80: # 80 because it overshoots a bit
                    radius = 0.33 # radius of the roundabout in meters
                    speed = 0.2 # speed for the roundabout in meters/second
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
            #time.sleep(0.05)
        print(f"% On roundabout, starting to turn.")




             # in degrees, TODO: assign a more accurate threshold for tilt
        # while not service.stop:
            # if self.state == 0:
            #     # approach roundabout
            #     service.send("robobot/cmd/ti", "rc 0.2 0.0")
            #     self.state = 1
            # elif self.state == 1:
            #     tilt = pose.pose[3]
            #     if self.some_condition():
            #         service.send("robobot/cmd/ti", "rc 0.0 0.0")
            #         self.state = 99
            # else:
            #     print(f"% RoundAbout complete")
            #     break
            # time.sleep(0.05)
