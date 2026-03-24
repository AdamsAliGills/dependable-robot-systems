from uservice import service
from see_saw import SeeSaw  
from sedge import edge
import time

def main():
    print("% Initializing system services...")
    service.setup('localhost')
    # Wait a moment to ensure the data stream from Teensy is OK
    time.sleep(1.0)
    
    try:
        #  Create the SeeSaw mission instance
        mission = SeeSaw()
        
        #  Start line following to approach the see-saw
        print("% Starting line control to find the see-saw...")
        edge.lineControl(0.2, followLeft=True)
        
        #  Execute the SeeSaw state machine
        success = mission.execute()
        
        if success:
            print("% See-saw mission completed successfully!")
        else:
            print("% Mission returned False (potentially stopped).")
    except KeyboardInterrupt:
        print("\n% User pressed Ctrl+C! Emergency stop initiated.")
    
    except Exception as e:
        print(f"% An unexpected error occurred: {e}")
    
    finally:
        print("% Cleaning up and stopping robot...")
        # Ensure motors are stopped by setting line control velocity to 0
        edge.lineControl(0) 
        # Send final stop commands and close MQTT threads
        service.terminate() 
        print("% System safely terminated.")

if __name__ == "__main__":
    main()