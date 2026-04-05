import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge

# --- PROJECT GENESIS : THE PROPHET (CHAOS PREDICTION ENGINE) ---
# Goal: Forecast the FUTURE of a chaotic time-series using BCN Physical Memory.
# Strategy: Mackey-Glass Chaos Injection -> Material State Capture -> Ridge Readout.

PORT = 'COM3' # Update!
BAUD = 115200

# 1. GENERATE CHAOS DATA (Mackey-Glass Equation)
def mackey_glass(sample_len=300, tau=17):
    y = [1.2] * sample_len
    for t in range(sample_len - 1):
        if t < tau:
            y[t+1] = y[t] + (0.2 * y[t] / (1 + y[t]**10) - 0.1 * y[t])
        else:
            y[t+1] = y[t] + (0.2 * y[t-tau] / (1 + y[t-tau]**10) - 0.1 * y[t])
    return np.array(y)

print("🌀 Generating Mackey-Glass Chaos Profile...")
raw_data = mackey_glass(300)
# Scale to 0-255 for Arduino PWM Input
data_in = ((raw_data - raw_data.min()) / (raw_data.max() - raw_data.min()) * 255).astype(int)

# Initialize Serial
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    print("✅ GENESIS Prophet Engine Online.")
except:
    print("❌ Connection Error. Check Serial/COM Port.")
    exit()

# 2. PHYSICAL INJECTION (Process through the BCN Reservoir)
reservoir_states = []
print("Injecting Chaos into BCN Lattice... (300 points)")

for val in data_in:
    # Send Stimulus (PWM byte)
    ser.write(bytes([val]))
    
    # Capture the 5D response vector
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if "DATA:" in line:
                data_str = line.split(":")[1]
                states = [int(v) for v in data_str.split(',')]
                reservoir_states.append(states)
                break

ser.close()

# 3. TRAINING THE READOUT LAYER (Ridge Regression)
print("Training Neural Readout for Time-Series Forecasting...")
X = np.array(reservoir_states[:-1]) # Input: Current Material State
y = raw_data[1:]                      # Target: Actual Value at next time step (t+1)

# Split into Train/Test
split = 200
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# Readout Model
readout = Ridge(alpha=1.0)
readout.fit(X_train, y_train)

# 4. PREDICTION & VALIDATION
y_pred = readout.predict(X_test)

# Calculate Score
score = readout.score(X_test, y_test)
print(f"✅ Forecasting Complete. Prediction Accuracy (R2): {score:.4f}")

# 5. VISUALIZATION
plt.style.use('dark_background')
plt.figure(figsize=(12, 6))
plt.plot(y_test, color='#FFD700', label='ACTUAL REALITY (Mackey-Glass)', linewidth=2)
plt.plot(y_pred, color='#00d1ff', linestyle='--', label='MATERIAL FORECAST (BCN Prophet)', linewidth=2)
plt.title(f"GENESIS BCN: CHAOS TIME-SERIES PREDICTION\nAccuracy: {score*100:.2f}%", size=15)
plt.xlabel("Time Step (t)")
plt.ylabel("Chaos Magnitude")
plt.grid(color='rgba(255,255,255,0.05)')
plt.legend()
plt.show()

print("\n--- [ THE PROPHET'S VERDICT ] ---")
if score > 0.8:
    print("🏆 GOD TIER : The material captures chaos perfectly.")
elif score > 0.5:
    print("🥈 STANDARD : Decent memory. Good for base tasks.")
else:
    print("⚠️ FAILED : No memory detected. Re-flash BCN cluster.")
print("---------------------------------")
