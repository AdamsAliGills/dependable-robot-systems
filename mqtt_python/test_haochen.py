import time
from uservice import service

class SensorTester:
    def __init__(self):
        self.raw_values = []
        self.norm_values = []
        self.got_data = False
        # Center of Gravity (COG) parameters
        self.lineValidThreshold = 750 
        self.low_limit = 650 # Threshold to filter background noise (lineValidThreshold - 100)
        self.line_pos = 0.0
        self.lineValid = False

    def decode(self, topic, msg):
        """
        Process sensor data and calculate the line position using COG.
        """
        if "T0/liv" in topic and "livn" not in topic:
            # Raw AD difference values (LSH - LSL)
            data = msg.split(" ")
            if len(data) >= 9:
                # Capture the 8 sensor channels
                self.raw_values = data[0:8]
                self.got_data = True
        elif "T0/livn" in topic:
            # Normalized values mapped to 0-1000
            data = msg.split(" ")
            if len(data) >= 9:
                # Extract normalized values (skip the first element which is the timestamp)
                self.norm_values = [int(x) for x in data[1:9]]
                self.got_data = True
                
                # Direct Center of Gravity (COG) calculation logic
                high = max(self.norm_values)
                self.lineValid = high >= self.lineValidThreshold
                
                if self.lineValid:
                    cog_sum = 0
                    pos_sum = 0
                    for i in range(8):
                        # Subtract background limit to eliminate low-level noise
                        v = self.norm_values[i] - self.low_limit
                        if v > 0:
                            cog_sum += v
                            # Weighted position: sensor index (1-8) * weight (v)
                            pos_sum += (i + 1) * v
                    
                    if cog_sum > 0:
                        # Map position to range -3.5 to 3.5
                        # (pos_sum / cog_sum) gives a value between 1.0 and 8.0
                        # Subtract 4.5 to center the range at 0
                        self.line_pos = (pos_sum / cog_sum) - 4.5

def run_test():
    # 1. Initialize the service.
    # Replace "localhost" with your robot's IP if necessary.
    service.setup("localhost")
    tester = SensorTester()
    
    # 2. Patch the service.decode method dynamically.
    original_decode = service.decode
    def patched_decode(topic, msg):
        # Run original robot logic
        original_decode(topic, msg)
        # Run custom testing and COG logic
        tester.decode(topic, msg)
        return True
    service.decode = patched_decode

    print("--- Sensor Hardware & COG Position Test ---")
    
    # 3. Enable line sensor: lip [on] [white_mode] [high_power]
    service.send("robobot/cmd/T0", "lip 1 0 1") 
    time.sleep(0.5) # Wait for hardware to stabilize

    # 4. Request data from the firmware
    service.send("robobot/cmd/T0", "livi") # Request raw values
    service.send("robobot/cmd/T0", "livni") # Request normalized values
    
    # 5. Wait for data to arrive via the background MQTT thread
    timeout = 3.0
    start_time = time.time()
    while time.time() - start_time < timeout:
        if len(tester.raw_values) > 0 and len(tester.norm_values) > 0:
            break
        time.sleep(0.1)

    # 6. Display the test results
    print("-" * 40)
    if len(tester.raw_values) > 0:
        print(f"Raw AD Values (LSH - LSL): \n{tester.raw_values}")
    else:
        print("Error: No raw data received. Is 'teensy_interface' running?")

    if len(tester.norm_values) > 0:
        print(f"\nNormalized Values (0-1000): \n{tester.norm_values}")
        
        # Output COG calculation results
        if tester.lineValid:
            print(f"Line Detected: YES")
            print(f"Line Position (COG): {tester.line_pos:.4f}")
            print(f"Note: Range is -3.5 (Left) to 3.5 (Right), 0 is Center")
        else:
            print(f"Line Detected: NO (Highest value below threshold {tester.lineValidThreshold})")
    else:
        print("Error: No normalized data. Calibration might be missing.")

    print("-" * 40)
    # 7. Shutdown: Turn off sensor to save power
    print("Test complete. Turning off LEDs.")
    service.send("robobot/cmd/T0", "lip 0")
    service.stop = True

if __name__ == "__main__":
    run_test()