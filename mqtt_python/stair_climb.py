from uservice import service
from sedge import edge
from sir import ir
import time
from detection_utils import wait_ramp_bottom, wait_ramp_top, wait_turn

def sleep(t):
    start = time.time()
    while (time.time() - start < t) and not service.stop:
        time.sleep(0.01)

class stairClimb():
    def __init__(self):
        pass

    def execute(self):
        print("% Stair climb: starting")
        edge.lineControl(0.15, True)

        service.send("robobot/cmd/T0", "servo 1 1 300")#activates the servo????
        for _ in range(5):

            # Step 1: move servo to straight position
            service.send("robobot/cmd/T0", "servo 1 -400 0")

            # Step 2: wait until first step is detected
            while not service.stop:
                if ir.ir[1] < 0.09:
                    break
                time.sleep(0.01)

            if service.stop:
                return False

            edge.lineControl(0)
            service.send("robobot/cmd/ti", "rc 0.0 0.0")
            service.send("robobot/cmd/T0", "servo 1 700 100")

            sleep(1.6)

            # Step 5: small forward movement
            service.send("robobot/cmd/ti", "rc 0.05 0.0")
            sleep(0.5)


            if service.stop:
                return False

            # Step 6: stronger forward
            service.send("robobot/cmd/ti", "rc 0.15 0.0")

            sleep(1)

        service.send("robobot/cmd/T0", "servo 1 -400 0")
        sleep(1)
        service.send("robobot/cmd/T0", "servo 1 10000 0")
        service.send("robobot/cmd/ti", "rc 0.0 0.0")

        if service.stop:
            return False

        print("% Stair climb: complete")
        return True

    def test(max_attempts: int):
        
        for i in range(max_attempts):
            print(f"Stair climb test {i} starting")
            s = stairClimb()
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