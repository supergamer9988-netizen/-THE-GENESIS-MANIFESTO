import serial
import time
import matplotlib.pyplot as plt
import numpy as np

# --- PROJECT GENESIS : HYSTERESIS ANALYZER (THE EUREKA SCAN) ---
# Goal: Detect "Pinched Hysteresis Loops" (The Fingerprint of Memory).
# Logic: Compare UP-SWEEP (0->255) vs DOWN-SWEEP (255->0).
# Result: If lines don't overlap, your material HAS MEMORY.

PORT = 'COM3' # Update!
BAUD = 115200

# Initialize Serial
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    print("✅ Hysteresis Engine Linked. Starting Dual-Sweep Calibration...")
except:
    print("❌ Serial Error.")
    exit()

input_history = []
output_history = []

# --- 1. THE SWEEP (UP -> DOWN) ---
print("Scanning Up (0->255)...")
for i in range(0, 256, 5):
    ser.write(bytes([i]))
    time.sleep(0.02)
    while ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line.startswith("DATA:"):
            vals = [int(v) for v in line.split(":")[1].split(',')]
            input_history.append(i)
            output_history.append(sum(vals)/len(vals))
            break

print("Scanning Down (255->0)...")
for i in range(255, -1, -5):
    ser.write(bytes([i]))
    time.sleep(0.02)
    while ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line.startswith("DATA:"):
            vals = [int(v) for v in line.split(":")[1].split(',')]
            input_history.append(i)
            output_history.append(sum(vals)/len(vals))
            break

# --- 2. ANALYSIS & VISUALIZATION ---
plt.style.use('dark_background')
plt.figure(figsize=(8, 8))

# Divide into Up/Down for coloring
midpoint = len(input_history) // 2
plt.plot(input_history[:midpoint], output_history[:midpoint], color='#00d1ff', label='UP SWEEP (Mem-Loading)', linewidth=2)
plt.plot(input_history[midpoint+1:], output_history[midpoint+1:], color='#ffd700', label='DOWN SWEEP (Mem-Decay)', linewidth=2)

plt.fill_between(input_history[:midpoint], output_history[:midpoint], output_history[midpoint+1:], color='white', alpha=0.1, label='HYSTERESIS AREA')

plt.xlabel('Input Voltage (Stimulus 0-255)')
plt.ylabel('Material Response (Conductance 0-1023)')
plt.title('GENESIS BCN: PINCHED HYSTERESIS LOOP ANALYSIS', size=14)
plt.grid(color='rgba(255,255,255,0.05)')
plt.legend()

print("\n--- [ THE EUREKA CHECK ] ---")
diff = np.mean(np.abs(np.array(output_history[:midpoint]) - np.array(output_history[midpoint+1:])))
print(f"Memory Gap (Mean Offset): {diff:.2f}")

if diff > 10:
    print("💎 EUREKA! PINCHED LOOP DETECTED. YOUR MATERIAL HAS MEMORY.")
else:
    print("⚠️ THIN LOOP. Material is too linear. Increase power or use 'Conditioning'.")
print("--------------------------")

plt.show()
ser.close()
