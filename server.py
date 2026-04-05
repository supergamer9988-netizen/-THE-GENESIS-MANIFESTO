from flask import Flask, request, jsonify
import serial
import json
import numpy as np
import time

# --- PROJECT GENESIS : SINGLE BLADE AI SERVER (server.py) ---
# Purpose: Expose 1x GENESIS Blade (16 Cores) as a calibrated AI endpoint.
# Requires: calibration.json (run calibrate.py first)
# Endpoint: POST /embed  {"text": "Hello GENESIS"}

app = Flask(__name__)

# --- HARDWARE SETUP ---
PORT = 'COM3'  # <-- Update to your ESP32 COM port
BAUD = 115200

# Load calibration data
try:
    with open('calibration.json', 'r') as f:
        cal = json.load(f)
    multipliers = np.array(cal['multipliers'])
    dead_cores  = cal.get('dead_cores', [])
    print(f"✅ Calibration loaded. Dead cores: {dead_cores or 'None'}")
except FileNotFoundError:
    print("⚠️ No calibration.json found. Run calibrate.py first!")
    print("   Using raw values (uncorrected).")
    multipliers = np.ones(16)
    dead_cores  = []

# Connect to board
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    print(f"✅ GENESIS Blade online at {PORT}")
    HARDWARE_MODE = True
except Exception as e:
    print(f"⚠️ Hardware offline — Simulation Mode active. ({e})")
    ser = None
    HARDWARE_MODE = False

def query_blade(stimulus: int) -> list:
    """Send stimulus to blade, return calibrated 16D vector."""
    if ser:
        ser.reset_input_buffer()
        ser.write(f"V:{stimulus}\n".encode())
        line = ser.readline().decode('utf-8', errors='ignore').strip()

        if line.startswith("DATA:"):
            raw = np.array([int(x) for x in line.split(":")[1].split(',')])

            # Apply per-core calibration multipliers
            corrected = raw * multipliers

            # Clamp to valid ADC range
            corrected = np.clip(corrected, 0, 4095)

            # Normalize to [0.0, 1.0]
            normalized = corrected / 4095.0

            # Zero out dead cores (don't let noise mislead the model)
            for dc in dead_cores:
                normalized[dc] = 0.0

            return normalized.tolist()

    # Simulation fallback: synthetic BCN hysteresis model
    x = np.linspace(0, np.pi, 16)
    sim = np.sin(x + (stimulus / 255.0)) * 0.5 + 0.5
    return sim.tolist()

# ─────────────────────────────────────────────
@app.route('/status')
def status():
    return jsonify({
        "system"          : "GENESIS-BLADE-V1",
        "hardware"        : HARDWARE_MODE,
        "port"            : PORT,
        "cores"           : 16,
        "dead_cores"      : dead_cores,
        "calibrated"      : True if multipliers.sum() != 16 else False
    })

@app.route('/embed', methods=['POST'])
def embed():
    """POST {"text": "Hello"} → 16D BCN vector"""
    body = request.get_json(force=True)
    text = body.get('text', '')
    if not text:
        return jsonify({"error": "text field required"}), 400

    stimulus = sum(ord(c) for c in text) % 256
    vector   = query_blade(stimulus)

    return jsonify({
        "text"    : text,
        "stimulus": stimulus,
        "vector"  : vector,
        "dim"     : len(vector),
        "mode"    : "hardware" if HARDWARE_MODE else "simulation"
    })

@app.route('/similarity', methods=['POST'])
def similarity():
    """Compare two texts → cosine similarity score"""
    body = request.get_json(force=True)
    a = body.get('a', '')
    b = body.get('b', '')

    va = np.array(query_blade(sum(ord(c) for c in a) % 256))
    vb = np.array(query_blade(sum(ord(c) for c in b) % 256))

    cos_sim = float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb) + 1e-9))

    return jsonify({"a": a, "b": b, "similarity": round(cos_sim, 4)})

# ─────────────────────────────────────────────
if __name__ == '__main__':
    print("🚀 GENESIS OS — Single Blade server starting on :5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
