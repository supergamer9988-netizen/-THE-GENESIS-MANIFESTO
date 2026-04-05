import serial
import time
import matplotlib.pyplot as plt
import numpy as np

# --- PROJECT GENESIS : HARDWARE DIAGNOSTICS (TRANSFER FUNCTION) ---
# Goal: Detect Impedance Mismatch, Linearity, and Noise Floor.
# Strategy: Send a Linear RAMP (0-255) and monitor Chip Response (0-1023).

PORT = 'COM3' # Update!
BAUD = 115200

# Initialize Serial
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2) # Delay for Arduino Reset
    print("✅ Diagnostic Engine Linked. Starting RAMP Test...")
except:
    print("❌ Connection Error. Check Serial Link.")
    exit()

input_vals = []
core_outputs = [[] for _ in range(5)] # Track all 5 cores separately

# Send Linear Ramp (0 -> 255)
steps = range(0, 256, 5)
print("Injecting Input Sweep (0-255)...")

for i in steps:
    # 1. Inject Data Byte
    ser.write(bytes([i]))
    time.sleep(0.05) # 50ms for thermal settling per step
    
    # 2. Scrape Response
    while ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line.startswith("DATA:"):
            # "DATA:512,120,40,10,0"
            data_str = line.split(":")[1]
            vals = [int(v) for v in data_str.split(',')]
            
            input_vals.append(i)
            # Store each core's response
            for core_idx, val in enumerate(vals):
                core_outputs[core_idx].append(val)
            
            # Print average to terminal
            avg_val = sum(vals) / 5
            print(f"RAMP IN: {i:3} | CLUSTER AVG: {avg_val:4.1f}")
            break

# 3. ANALYSIS & VISUALIZATION
plt.style.use('dark_background')
plt.figure(figsize=(10, 6))

colors = ['#00d1ff', '#00ff00', '#ffd700', '#ff00ff', '#ff4500']
for core_idx in range(5):
    plt.plot(input_vals, core_outputs[core_idx], 'o-', 
             label=f'Core {core_idx}', color=colors[core_idx], alpha=0.7)

plt.xlabel('Input Signal (PWM 0-255)')
plt.ylabel('Chip Response (Analog 0-1023)')
plt.title('GENESIS BC: TRANSFER FUNCTION ANALYSIS (RAMP TEST)')
plt.grid(color='rgba(255,255,255,0.1)')
plt.legend()

print("\n--- [ DIAGNOSIS GUIDE ] ---")
print(" 1. FLATLINE @ 0/1023 : Impedance Mismatch (Check Resistors).")
print(" 2. PERFECT DIAGONAL  : Too Linear (Increase Voltage/Re-Flash).")
print(" 3. NON-LINEAR CURVE  : GOD TIER FOUND (Material Ready for RNC).")
print("--------------------------")

plt.show()
ser.close()
