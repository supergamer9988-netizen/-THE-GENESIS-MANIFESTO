import serial
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import time

# --- PROJECT GENESIS : COMPUTATIONAL MATH ENGINE (PHYSICAL RNC) ---
# Goal: Test the 5-Core BCN Cluster's ability to map Sin -> Cos via Material Memory.
# Strategy: Reservoir Computing (Fixed Physical Weights + Linear Readout).

PORT = 'COM3' # Update!
BAUD = 115200

# 1. GENERATE TRAINING DATA
t = np.linspace(0, 4 * np.pi, 200) # 2 Full Sine cycles
input_signal = (np.sin(t) + 1) / 2 * 255 # 0-255 Input
target_signal = (np.cos(t) + 1) / 2 * 255 # Expected Cosine Target

# Initialize Serial
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2) # Arduino Reset Delay
    print("✅ GENESIS Math Engine Online.")
except:
    print("❌ Serial Error. Check COM Port.")
    exit()

# 2. RUN PHYSICAL INFERENCE (Inject Data into BCN)
reservoir_states = []
print("Injecting data into BCN Lattice... (Processing 200 samples)")

for val in input_signal:
    # Send byte to Arduino -> BCN Data Bus
    ser.write(bytes([int(val)]))
    
    # Read the 5D response frame
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith("DATA:"):
                # "DATA:512,120,40,10,0" -> [512, 120, 40, 10, 0]
                data_str = line.split(":")[1]
                core_values = [int(v) for v in data_str.split(',')]
                reservoir_states.append(core_values)
                break

# 3. TRAINING THE READOUT LAYER (Linear Regression)
print("Training AI Readout Layer...")
X = np.array(reservoir_states)
y = np.array(target_signal)

# Model: Reservoir Computing approach leverages the material's NON-LINEAR transformation.
reg = LinearRegression()
reg.fit(X, y)
forecast = reg.predict(X)

score = reg.score(X, y)
print(f"✅ Calculation Successful. R2 Precision: {score:.4f}")

# 4. VISUALIZATION
plt.style.use('dark_background')
plt.figure(figsize=(12, 7))
plt.plot(target_signal, label='IDEAL Target (Cosine)', color='#FFD700', linestyle='--', alpha=0.6)
plt.plot(forecast, label='MATERIAL Output (GENESIS BCN)', color='#00d1ff', linewidth=2)
plt.title(f"GENESIS BCN: NON-LINEAR MATH ENGINE (Sin -> Cos)\nPrecision: {score*100:.2f}%", size=15)
plt.xlabel("Time Step (t)")
plt.ylabel("Signal Amplitude (0-255)")
plt.grid(color='rgba(255,255,255,0.05)')
plt.legend()
plt.show()

ser.close()
