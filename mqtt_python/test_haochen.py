import time
from uservice import service

class SensorTester:
    def __init__(self):
        self.raw_values = []
        self.norm_values = []
        self.got_data = False

    def decode(self, topic, msg):
        """
        Callback to process incoming sensor data.
        Note: In uservice.py, the 'topic' passed here is usually the subtopic.
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
                self.norm_values = data[0:8]
                self.got_data = True

def run_test():
    # 1. Initialize the service. This converts service.client from a list [] 
    # into a real MQTT Client object.
    # Replace "localhost" with your robot's IP if necessary.
    service.setup("localhost")
    
    # 2. Create our tester instance
    tester = SensorTester()
    
    # 3. Patch the service.decode method dynamically.
    # Since 'subs' does not exist in uservice.py, 
    # we wrap the original decode function to also call our tester.
    original_decode = service.decode
    
    def patched_decode(topic, msg):
        # Run original robot logic (IMU, Pose, etc.)
        used = original_decode(topic, msg)
        
        # Run our custom testing logic
        tester.decode(topic, msg)
        return used

    # Inject the patched method back into the service instance
    service.decode = patched_decode

    print("--- Starting Sensor Hardware Test ---")
    
    # 4. Wait for MQTT connection to be established
    while not service.connected:
        print("Connecting to MQTT Broker...")
        time.sleep(0.5)

    # 5. Enable line sensor: lip [on] [white_mode] [high_power]
    # Parameters: 1 (on), 0 (black line mode), 1 (high power mode)
    service.send("robobot/cmd/T0", "lip 1 0 1") 
    print("Command sent: Line Sensor ON (High Power)")
    time.sleep(0.5) # Wait for hardware and power to stabilize

    # 6. Request data from the firmware
    # 'livi' triggers a raw AD value ('liv') response
    print("\n[1/2] Requesting raw AD values (livi)...")
    service.send("robobot/cmd/T0", "livi")
    
    # 'livni' triggers a normalized value ('livn') response
    print("[2/2] Requesting normalized values (livni)...")
    service.send("robobot/cmd/T0", "livni")
    
    # 7. Wait for data to arrive via the background MQTT thread
    timeout = 3.0
    start_time = time.time()
    while time.time() - start_time < timeout:
        if len(tester.raw_values) > 0 and len(tester.norm_values) > 0:
            break
        time.sleep(0.1)

    # 8. Display the test results
    print("-" * 40)
    if len(tester.raw_values) > 0:
        print(f"Raw AD Values (LSH - LSL): \n{tester.raw_values}")
    else:
        print("Error: No raw data received. Is 'teensy_interface' running?")

    if len(tester.norm_values) > 0:
        print(f"\nNormalized Values (0-1000): \n{tester.norm_values}")
    else:
        print("Error: No normalized data. Calibration might be missing.")

    # 9. Shutdown: Turn off sensor to save power
    print("-" * 40)
    print("Test complete. Turning off LEDs.")
    service.send("robobot/cmd/T0", "lip 0")
    
    # Optional: Stop service threads
    service.stop = True

if __name__ == "__main__":
    # The UService starts background threads automatically when setup() is called
    run_test()