import serial
import time
import matplotlib.pyplot as plt
import sys

# --- PROJECT GENESIS : LIVE HYSTERESIS PLOTTER (THE MEMORY LOOP) ---
# Goal: Visualize the non-linear "Leaf" pattern of your BCN Memristor.
# Success Indicator: A LOOP (Up and down paths are separate).

PORT = 'COM3' # Update!
BAUD = 115200

# Initialize Serial
try:
    ser = serial.Serial(PORT, BAUD, timeout=2)
    time.sleep(2) # Arduino Reset Delay
    print(f"✅ Linked to GENESIS CLUSTER on {PORT}")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    sys.exit()

# Data Collection buffers
inputs_x = []  
outputs_y = [] 

print("🚀 SCANNING GENESIS MEMORY POOL...")
ser.write(b'S') # Command: START DATA SWEEP

while True:
    try:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        
        if line == "END":
            break # Frame complete
            
        if "," in line:
            parts = line.split(',')
            pwm = int(parts[0])
            analog = int(parts[1])
            
            inputs_x.append(pwm)
            outputs_y.append(analog)
            
            # Live Terminal readout
            print(f"V_In: {pwm:3} | V_Out: {analog:4}")
            
    except ValueError:
        pass

ser.close()

# --- THE BCN VERDICT: PLOTTING ---
print("\n📊 PLOTTING HYSTERESIS LATTICE...")
plt.style.use('dark_background')
plt.figure(figsize=(10, 8))

# Draw the main Loop Path
plt.plot(inputs_x, outputs_y, color='#00d1ff', linewidth=3, label='BCN Memory Path (Hysteresis)')

# Highlight critical points (Start, Peak, End)
if inputs_x:
    midpoint = len(inputs_x) // 2
    plt.plot(inputs_x[0], outputs_y[0], 'go', markersize=12, label='Start (0V State)') # Green
    plt.plot(inputs_x[midpoint], outputs_y[midpoint], 'ro', markersize=12, label='Peak (5V Saturated)') # Red
    plt.plot(inputs_x[-1], outputs_y[-1], 'yo', markersize=8, label='Remanence (Mem-Lock)') # Yellow

plt.title('PROJECT GENESIS: BCN HYSTERESIS LOOP (PROOF OF INTEL)', size=16, color='gold')
plt.xlabel('Stimulus (PWM Input 0-255)', size=12)
plt.ylabel('Conductance (Analog Response 0-1023)', size=12)
plt.grid(color='rgba(255,255,255,0.05)')
plt.legend()

print("\n--- [ HOW TO READ ] ---")
print(" 1. LOOP (LEAF SHAPE): SUCCESS. Material remembers past states (Memristor).")
print(" 2. SINGLE LINE: RETRAIN. Material is purely linear (Standard Resistor).")
print("--------------------------")

plt.show()
