from uservice import service
from spose import pose
import time

class roundAbout():
    def __init__(self):
        self.name = "RoundAbout"
        self.state = 0
        start_time = time.time()
        while time.time() - start_time < 15:  # Run for 15 seconds
            self.get_tilt()
            time.sleep(0.1)  # optional: prevent 100% CPU usage
                
        

    

    def get_tilt(self):
        print(pose.pose[3])


    def execute(self):
        """Call this repeatedly from a loop - non-blocking state machine"""
        while not service.stop:
            if self.state == 0:
                # approach roundabout
                service.send("robobot/cmd/ti", "rc 0.2 0.0")
                self.state = 1
            elif self.state == 1:
                tilt = pose.pose[3]
                if self.some_condition():
                    service.send("robobot/cmd/ti", "rc 0.0 0.0")
                    self.state = 99
            else:
                print(f"% RoundAbout complete")
                break
            time.sleep(0.05)