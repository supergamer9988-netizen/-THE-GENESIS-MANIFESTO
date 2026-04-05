import serial
import time
import json
import numpy as np

# --- PROJECT GENESIS : HARDWARE EQUALIZER (calibrate.py) ---
# Purpose: Measure each Core's baseline resistance & create correction multipliers.
# Run ONCE after first insertion of BCN graphite cores.
# Output: calibration.json (the board's "Medical Certificate")

PORT    = 'COM3'   # <-- Update to your ESP32 COM port
BAUD    = 115200
SAMPLES = 50       # Higher = more accurate baseline

print("====================================")
print("  GENESIS BLADE - CALIBRATION MODE ")
print("====================================")

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(3)
    print(f"✅ Connected to GENESIS Blade on {PORT}")
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    exit()

# Step 1: Preheat (Burn-in)
print("\n🔥 Preheating cores (2 seconds @100%)...")
ser.write(b"CALIBRATE\n")
time.sleep(2)

# Step 2: Baseline Sweep
print(f"📊 Measuring baseline across {SAMPLES} samples @V:128 (50%)...")
baseline_readings = []

for i in range(SAMPLES):
    ser.reset_input_buffer()
    ser.write(b"V:128\n")
    line = ser.readline().decode('utf-8', errors='ignore').strip()

    if line.startswith("DATA:"):
        vals = [int(x) for x in line.split(":")[1].split(',')]
        baseline_readings.append(vals)
        print(f"  Sample {i+1:02d}/{SAMPLES}: {vals[:4]}...  ", end='\r')
    time.sleep(0.06)

print("\n")

if len(baseline_readings) < 5:
    print("❌ Insufficient data. Check board connection and firmware.")
    exit()

# Step 3: Compute Correction Multipliers
avg_baseline = np.mean(baseline_readings, axis=0)
std_baseline = np.std(baseline_readings, axis=0)

print("--- BASELINE REPORT (Core Resistance Profile) ---")
dead = []
for i, (avg, std) in enumerate(zip(avg_baseline, std_baseline)):
    flag = ""
    if avg < 100:
        flag = "  ⚠️ DEAD / OPEN CIRCUIT"
        dead.append(i)
    elif avg > 3950:
        flag = "  ⚠️ SHORT CIRCUIT"
        dead.append(i)
    print(f"  Core-{i:02d}: Mean={avg:7.1f}  Std={std:5.1f}{flag}")

if dead:
    print(f"\n⚠️ WARNING: Cores {dead} show anomalies. Check clips and BCN insertion.")

# Target = highest recorded clean value (normalize up to match best core)
clean_baseline = np.where(avg_baseline < 100, np.nan, avg_baseline)
clean_baseline = np.where(clean_baseline > 3950, np.nan, clean_baseline)
target_val = np.nanmax(clean_baseline)

# Multipliers: scale every core up to the target
multipliers = np.where(avg_baseline > 0, target_val / avg_baseline, 1.0)

# Step 4: Save
cal_data = {
    "port"       : PORT,
    "timestamp"  : time.time(),
    "samples"    : SAMPLES,
    "target"     : float(target_val),
    "baseline"   : avg_baseline.tolist(),
    "std_dev"    : std_baseline.tolist(),
    "multipliers": multipliers.tolist(),
    "dead_cores" : dead
}

with open('calibration.json', 'w') as f:
    json.dump(cal_data, f, indent=2)

print(f"\n✅ calibration.json saved. Target level: {target_val:.0f}/4095")
print(f"   Board Health: {16 - len(dead)}/16 cores CLEAN")
print("\n🏁 Calibration complete. Run server.py next.")

ser.write(b"SLEEP\n")
ser.close()
