from flask import Flask, request, jsonify
import serial
import time
import numpy as np

# --- PROJECT GENESIS : GLOBAL AI SERVER (GENESIS-OS V1.0) ---
# Goal: Expose the 16-Core BCN Blade Cluster via a public API.
# Logic: External Web Request -> COM Dispatch -> BCN Vectorization -> JSON Response.

app = Flask(__name__)

# --- HARDWARE LINK ---
PORT = 'COM3' # Update to ESP32 Port
BAUD = 115200

# Try connecting to the Physical Rack
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    print("✅ GENESIS Blade V1.0 - Hardware Cluster ONLINE.")
except:
    print("⚠️ Hardware Rack Offline - Entering Virtual Simulation Mode (V-BCN).")
    ser = None

@app.route('/')
def index():
    return jsonify({
        "status": "ONLINE" if ser else "SIMULATED",
        "model": "GENESIS-BLADE-V1",
        "cores": 16,
        "endpoint": "/vectorize",
        "auth": "GOD-TIER-LEVEL-0"
    })

@app.route('/vectorize', methods=['POST'])
def vectorize():
    """
    POST Request Body: { "text": "Hello World" }
    Returns: 16-Dimensional BCN Embedding Vector.
    """
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "No input text provided."}), 400
    
    text_input = data['text']
    stimulus = sum([ord(c) for c in text_input]) % 256
    
    print(f"🧬 Vectorizing input: '{text_input}' | Stimulus: {stimulus}V")
    
    # 1. Send to Blade Rack
    if ser:
        ser.write(bytes([stimulus]))
        
        # 2. Wait for 16-Core Response
        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if "BLADE:" in line:
                    parts = line.split(":")[1].split(',')
                    vector = [int(p) for p in parts]
                    break
    else:
        # Simulation Mode: Synthetic BCN Hysteresis Mapping
        # Map: y = sin(stimulus/255 * PI) + Noise
        base = np.sin(np.linspace(0, np.pi, 16) + (stimulus/255))
        noise = np.random.normal(0, 0.05, 16)
        vector = (np.clip(base + noise, 0, 1) * 1023).astype(int).tolist()

    return jsonify({
        "input": text_input,
        "stimulus_code": stimulus,
        "vector": vector,
        "dimension": 16,
        "timestamp": time.time(),
        "hardware_verified": True if ser else False
    })

if __name__ == '__main__':
    print("🚀 GENESIS OS: Bio-Digital AI Gateway starting on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
