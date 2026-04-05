import serial
import time
import numpy as np
import matplotlib.pyplot as plt

# --- PROJECT GENESIS : RNC STABILIZER & ENTROPY SCANNER ---
# Goal: Find the "Sweet Spot" (Dynamic Range) for your BCN Cluster.
# Logic: Scan different Voltage Intervals (Masking) and calculate the Variance (Entropy).
# Result: Maximum Entropy = Best Computational Reservoir.

PORT = 'COM3' # Update!
BAUD = 115200

# Initialize Serial
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    print("✅ GENESIS Stability Engine Online. Identifying Reservoir Entropy...")
except:
    print("❌ Serial Error.")
    exit()

ranges = [50, 100, 150, 200, 255] # Peak PWM amplitudes to test
entropy_scores = []
readings_store = []

print("Scanning Dynamic Ranges for Maximum Non-linearity...")

for peak in ranges:
    print(f"Testing Profile: 0 -> {peak} PWM...")
    local_readings = []
    
    # Sweep through the range
    for i in range(0, peak, 10):
        ser.write(bytes([i]))
        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if "PRECISION:" in line:
                    vals = [int(p) for p in line.split(":")[1].split(',')]
                    local_readings.append(np.mean(vals))
                    break
    
    # Calculate "Entropy" (Standard Deviation of the Transfer Function's Curve Change)
    # Higher variance in the *derivative* of the curve = more non-linear features.
    diffs = np.diff(local_readings)
    entropy = np.std(diffs)
    entropy_scores.append(entropy)
    readings_store.append(local_readings)

# --- RESULTS & OPTIMIZATION ---
best_idx = np.argmax(entropy_scores)
best_pwm = ranges[best_idx]

print("\n--- [ STABILITY VERDICT ] ---")
print(f"Optimal Operating Range: 0 to {best_pwm} PWM")
print(f"Peak Neural Entropy: {entropy_scores[best_idx]:.4f}")

if entropy_scores[best_idx] > 2.0:
    print("💎 GOLDEN RESERVOIR: High complexity detected. Compute ready.")
else:
    print("⚠️ LINEAR TRAP: Material is too resistive/conductive. Adjust R_series.")
print("----------------------------")

# --- VISUALIZATION ---
plt.style.use('dark_background')
plt.figure(figsize=(10, 6))

for i, profile in enumerate(readings_store):
    plt.plot(profile, label=f"Range 0-{ranges[i]} (Entropy: {entropy_scores[i]:.2f})")

plt.title("PROJECT GENESIS: RESERVOIR ENTROPY CALIBRATION", size=15)
plt.xlabel("Step Index")
plt.ylabel("Analog Response (Conductance)")
plt.legend()
plt.grid(color='rgba(255,255,255,0.05)')
plt.show()

ser.close()
