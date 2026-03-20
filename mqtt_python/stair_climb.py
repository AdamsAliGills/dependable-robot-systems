from uservice import service
from sedge import edge
from sir import ir
import time

def sleep(t):
    start = time.time()
    while (time.time() - start < t) and not service.stop:
        time.sleep(0.01)

class stairClimb():
    def __init__(self):
        pass

    def execute(self):
        print("% Stair climb: starting")
        edge.lineControl(0.2, True)

        # Step 1: move servo to straight position
        service.send("robobot/cmd/T0", "servo 1 1 300")#activates the servo????
        service.send("robobot/cmd/T0", "servo 1 -400 300")

        # Step 2: wait until first step is detected
        while not service.stop:
            if ir.ir[1] < 0.09:
                break
            time.sleep(0.01)

        if service.stop:
            return

        edge.lineControl(0)
        service.send("robobot/cmd/ti", "rc 0.0 0.0")
        service.send("robobot/cmd/T0", "servo 1 700 100")

        sleep(0.5)

        if service.stop:
            return

        # Step 5: small forward movement
        service.send("robobot/cmd/ti", "rc 0.05 0.0")
        sleep(1.5)

        if service.stop:
            return

        # Step 6: stronger forward + reset servo
        service.send("robobot/cmd/ti", "rc 0.2 0.0")

        sleep(0.5)
        service.send("robobot/cmd/T0", "servo 1 -400 0")

        while not service.stop:
            pass

        print("% Stair climb: complete")