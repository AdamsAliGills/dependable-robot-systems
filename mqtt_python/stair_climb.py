from uservice import service
from sedge import edge
from sir import ir
import time

class stairClimb():
    def __init__(self):
        '''Constructor for the stair climb mission'''
        self.state = 0
                
        while not service.stop:
            print(f"ir: {ir.ir[1]}")
     
    def execute(self):
        """Call this repeatedly from a loop - non-blocking self.state machine"""
        print("% Stair climb: starting")
        while not service.stop:
            
            if self.state == 0:
                # move servo to straight position
                service.send("robobot/cmd/T0", "servo 1 -150 300")
                self.state = 1
            elif self.state == 1:  # wait until first step is detected
                if ir.ir[0] < 0.09:
                    # only move straight
                    edge.lineControl(0)
                    service.send("robobot/cmd/ti", "rc 0.2 0.0")
                    # move servo down
                    service.send("robobot/cmd/T0", "servo 1 -700 300")
                    self.state = 2

            else:
                
                print("% Stair climb: complete")
                break
            time.sleep(0.05)

