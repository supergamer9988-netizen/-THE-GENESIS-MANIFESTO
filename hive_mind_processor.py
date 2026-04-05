import serial
import numpy as np
import time

# --- PROJECT GENESIS : HIVE MIND PROCESSOR ---
# Goal: Aggregate data from 5 BCN Cells in parallel 
# Applications: Majority Voting, Deep Reservoir, Parallel Vision

SERIAL_PORT = 'COM3' # Update!
BAUD_RATE = 115200

def process_hive_data(raw_frame):
    """Convert raw MUX data into a 5D Parallel State"""
    try:
        data = raw_frame.split("HIVE:")[1]
        vals = [int(v) for v in data.split(',')]
        return np.array(vals)
    except:
        return None

def majority_vote(vector):
    """Democracy Logic: Threshold all values and take the mode"""
    threshold = 512
    votes = [1 if v > threshold else 0 for v in vector]
    return 1 if sum(votes) >= 3 else 0

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2)
    print("--- [ GENESIS : HIVE MIND ACTIVE ] ---")
    print("Capturing 5 Parallel States [C0, C1, C2, C3, C4]")

    while True:
        line = ser.readline().decode('utf-8').strip()
        if "HIVE:" in line:
            state = process_hive_data(line)
            if state is not None:
                # 1. Majority Voting Concept
                decision = majority_vote(state)
                
                # 2. Entropy / Diversity Check (Variability of Cores)
                std_dev = np.std(state)
                
                # Visualization (ASCII Sparklines)
                spark = "".join(['#' if v > 512 else '.' for v in state])
                print(f"[{spark}] Output: {decision} | Diversity: {std_dev:.2f} | Cores: {state}")
                
        time.sleep(0.01)

except Exception as e:
    print(f"Blink Error: {e}")

print("Hive Closed.")
