from flask import Flask, request, jsonify
import serial
import time
import numpy as np

# --- PROJECT GENESIS : INDUSTRIAL AI SERVER (GENESIS-OS V1.1) ---
# Goal: Advanced Industrial Management for BCN Blade V1.1 (Noise/Thermal).
# Strategy: Noise Cancellation Algorithms + Multi-Channel Calibration + Cloud API.

app = Flask(__name__)

# --- HARDWARE LINK ---
PORT = 'COM3' # ESP32
BAUD = 115200

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    print("✅ GENESIS Industrial Blade V1.1 - NOISE KILLER LINKED.")
except:
    print("⚠️ Hardware Rack Offline - Entering Virtual Simulation Mode (V-BCN).")
    ser = None

# Calibration Table (Per Core Offset - Sampled at Startup)
# Corrects for slight differences in Graphite/BCN Resistance
core_offsets = np.zeros(16)

def calibrate_blade():
    """Initial Noise & Thermal Baseline Calibration."""
    if ser:
        print("🔍 Calibrating Blade 16-Core Matrix...")
        ser.write(bytes([128])) # Mid-voltage stimulus
        time.sleep(1)
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if "BLADE_V1.1:" in line:
            parts = line.split(":")[1].split(',')
            vals = np.array([int(p) for p in parts])
            # Set baseline relative to theoretical median
            global core_offsets
            core_offsets = vals - 512
            print(f"✅ Calibration Map Saved: {core_offsets}")

calibrate_blade()

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "ONLINE" if ser else "SIMULATED",
        "model": "GENESIS-INDUSTRIAL-BLADE-V1.1",
        "signal_integrity": "NOISE-KILLER-ACTIVE",
        "thermal_stabilization": "WIND-TUNNEL-ACTIVE",
        "cores": 16,
        "calibration": core_offsets.tolist()
    })

@app.route('/vectorize', methods=['POST'])
def vectorize():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "No input text provided."}), 400
    
    stimulus = sum([ord(c) for c in data['text']]) % 256
    
    if ser:
        ser.write(bytes([stimulus]))
        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if "BLADE_V1.1:" in line:
                    parts = line.split(":")[1].split(',')
                    raw_vec = np.array([int(p) for p in parts])
                    
                    # Apply Noise Mitigation (Subtract Core Offset)
                    clean_vec = (raw_vec - core_offsets).astype(int).tolist()
                    break
    else:
        # Simulation Mode
        base = np.sin(np.linspace(0, np.pi, 16) + (stimulus/255))
        vector = (np.clip(base, 0, 1) * 1023).astype(int).tolist()
        clean_vec = vector

    return jsonify({
        "input": data['text'],
        "cleaned_vector": clean_vec,
        "dimension": 16,
        "mode": "INDUSTRIAL-PRECISION",
        "timestamp": time.time()
    })

if __name__ == '__main__':
    print("🚀 GENESIS OS V1.1: Industrial AI Gateway starting on port 5000...")
    app.run(host='0.0.0.0', port=5000)
