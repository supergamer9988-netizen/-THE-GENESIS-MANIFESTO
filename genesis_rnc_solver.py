import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge

# --- PROJECT GENESIS : RNC SOLVER (NON-LINEAR FUNCTION APPROXIMATOR) ---
# Goal: Solve complex math y = 0.5x^2 + sin(5x) using Physical Reservoir Computing.
# Strategy: Virtual Nodes (Time Multiplexing) + BCN Material Dynamics + Ridge Readout.

PORT = 'COM3' # Update!
BAUD = 115200
VIRTUAL_NODES = 20 # 1 Physical Core simulated as 20 Virtual Neurons
MASK_LEN = VIRTUAL_NODES

# Initialize Serial
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    print("✅ GENESIS RNC Engine Online. Igniting Virtual Neurons...")
except:
    print("❌ Hardware Error. Ensure BCN Cluster is linked.")
    exit()

# 1. GENERATE MASK (Input Pre-processing)
# Random weights to jitter the input and trigger different lattice reactions.
np.random.seed(42)  # For reproducibility
mask = np.random.choice([-1, 1], size=(5, MASK_LEN))

def get_reservoir_state(input_val):
    """
    RNC Core Logic: 
    Input -> Time-Multiplexed Stimulus -> Multi-Core Sampling -> State Vector.
    """
    states = []
    
    for i in range(MASK_LEN):
        # Apply mask to jitter input (0.0 - 1.0)
        # We invert the stimulus based on mask to trigger dual-hysteresis paths
        pwm_val = int(input_val * 255)
        if mask[0][i] == -1:
            pwm_val = 255 - pwm_val
            
        # Send Stimulus
        ser.write(bytes([pwm_val]))
        
        # Read Response from 5 Cores (PRECISION Format)
        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if "PRECISION:" in line:
                    parts = line.split(":")[1].split(',')
                    core_readings = [int(p) for p in parts]
                    states.extend(core_readings) # Concatenate readings (High-dim vector)
                    break
    return np.array(states)

# 2. GENERATE THE MATH PUZZLE (Target Equation)
# Non-linear function: 0.5x^2 + sin(5x)
X_pts = np.linspace(0, 1, 100) # Input values
y_target = 0.5 * X_pts**2 + np.sin(5 * X_pts)

# 3. HARVESTING TRAINING DATA
print("🧠 Injecting Math Logic into BCN Lattice...")
X_states = []

for x in X_pts:
    state = get_reservoir_state(x)
    X_states.append(state)
    print(".", end='', flush=True)

print(f"\n✅ Harvest Complete. Feature Space: {len(X_states[0])} dimensions.")

# 4. TRAINING THE READOUT (Ridge Regression)
split = 80 # Train on 80%, Test on 20%
X_train, X_test = X_states[:split], X_states[split:]
y_train, y_test = y_target[:split], y_target[split:]

print("⚙️ Training Neural Readout (Ridge Solver)...")
readout = Ridge(alpha=1e-3)
readout.fit(X_train, y_train)

# 5. PREDICTION & PLOTTING
y_pred = readout.predict(X_test)
error = np.mean(np.square(y_test - y_pred))

print(f"📊 Accuracy Score (MSE): {error:.6f}")

plt.style.use('dark_background')
plt.figure(figsize=(12, 7))
# Full Target Curve
plt.plot(range(0, 100), y_target, color='rgba(255,255,255,0.2)', label='FULL TARGET CURVE')
# Test Result Comparison
plt.plot(range(split, 100), y_test, color='#FFD700', label='REALITY (Target Equation)', linewidth=3)
plt.plot(range(split, 100), y_pred, color='#00d1ff', linestyle='--', label='BCN PREDICTION (RNC Solution)', linewidth=2)

plt.title(f"GENESIS BCN: RNC MATH SOLVER\nTask: $y = 0.5x^2 + \\sin(5x)$ | Error: {error:.6f}", size=16)
plt.xlabel("Input X (Temporal Sequence)", size=12)
plt.ylabel("Result Y (Mapped State)", size=12)
plt.legend()
plt.grid(color='rgba(255,255,255,0.05)')
plt.show()

ser.close()
