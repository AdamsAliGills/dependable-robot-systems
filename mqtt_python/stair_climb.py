from uservice import service
from sedge import edge
from sir import ir
import time
from detection_utils import wait_ramp_bottom, wait_ramp_top, wait_turn

def sleep(t):
    start = time.time()
    while (time.time() - start < t) and not service.stop:
        time.sleep(0.01)

class StairClimb():
    def __init__(self):
        pass

    def execute(self):
        
        service.send("robobot/cmd/T0", "servo 1 1 10")
        print("% Stair climb: starting")
        edge.lineControl(0.15, True)

        for _ in range(5):

            # Step 1: move servo to straight position
            service.send("robobot/cmd/T0", "servo 1 -400 0")
            
            # Step 2: wait until first step is detected
            while not service.stop:
                if ir.ir[1] < 0.08:
                    break
                time.sleep(0.01)
            service.send("robobot/cmd/T0", "servo 3 265 0")
            edge.lineControl(0)

            service.send("robobot/cmd/ti", "rc 0.05 0.0")
            sleep(3)

            if service.stop:
                return False

            #edge.lineControl(0)
            #service.send("robobot/cmd/ti", "rc 0.0 0.0")
            service.send("robobot/cmd/T0", "servo 1 800 100")

            sleep(4)


            if service.stop:
                return False

            # Step 6: stronger forward
            service.send("robobot/cmd/ti", "rc 0.25 0.0")
            service.send("robobot/cmd/T0", "servo 1 -400 0")

            sleep(2)
            service.send("robobot/cmd/ti", "rc 0.0 0.0")
            service.send("robobot/cmd/T0", "servo 3 700 100")
            #service.send("robobot/cmd/T0", "servo 1 -400 0")
            sleep(2.5)
            #edge.lineControl(0.05)
            service.send("robobot/cmd/ti", "rc 0.05 0.0")

            sleep(0.85)

        service.send("robobot/cmd/T0", "servo 1 -400 0")
        sleep(0.5)
        service.send("robobot/cmd/ti", "rc 0.0 0.0")
        service.send("robobot/cmd/T0", "servo 3 265 0")

        if service.stop:
            return False

        print("% Stair climb: complete")
        return True

    def test(max_attempts: int):
        
        for i in range(max_attempts):
            print(f"Stair climb test {i} starting")
            s = StairClimb()
            results = s.execute()

            if results:
                print(f"Stair climb test {i} successful")
            else:
                print(f"Stair climb test {i} gone wrong")
                return i

            edge.lineControl(0.2, followLeft=True)
            
            wait_ramp_top(15, tolerance = 3)
            if service.stop:
                return i

            wait_ramp_bottom(15, tolerance = 3)
            if service.stop:
                return i

            wait_turn(160)
            if service.stop:
                return i

        return max_attempts