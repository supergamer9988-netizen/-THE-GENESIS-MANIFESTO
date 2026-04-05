from flask import Flask, request, jsonify
import serial
import time
import numpy as np

# --- PROJECT GENESIS : GLOBAL AI SERVER (PRODUCTION-V1.0) ---
# Goal: High-Availability API for the 16-Core GENESIS Production Blade.
# Command Syntax: Serial.write("V:128\n") -> Receive "DATA:10,20,30..."

app = Flask(__name__)

# --- HARDWARE LINK (COM4 / ESP32) ---
PORT = 'COM3' 
BAUD = 115200

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    print("✅ GENESIS PRODUCTION RACK - ONLINE.")
except:
    print("⚠️ Hardware Link Error - Simulation Mode Enabled.")
    ser = None

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "device": "GENESIS-BLADE-V1",
        "status": "READY" if ser else "SIMULATED",
        "hardware_verified": True if ser else False
    })

@app.route('/preheat', methods=['GET'])
def preheat():
    """Thermal Calibration Trigger."""
    if ser:
        ser.write(b"CALIBRATE\n")
        return jsonify({"status": "CORE_PREHEATING_ACTIVE"})
    return jsonify({"error": "Hardware offline."})

@app.route('/vectorize', methods=['POST'])
def vectorize():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "No input text provided."}), 400
    
    # 1. Map Text to Stimulus (0-255)
    stimulus = sum([ord(c) for c in data['text']]) % 256
    
    # 2. Hardware Dispatch (V:X format)
    if ser:
        ser.write(f"V:{stimulus}\n".encode())
        
        # Wait for Production DATA packet
        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if "DATA:" in line:
                    parts = line.split(":")[1].split(',')
                    vector = [int(p) for p in parts]
                    break
    else:
        # Simulation Mode: 16D Sine Hysteresis
        vector = (np.sin(np.linspace(0, np.pi, 16) + (stimulus/255)) * 1023).astype(int).tolist()

    return jsonify({
        "input": data['text'],
        "stimulus": stimulus,
        "vector_16d": vector,
        "timestamp": time.time()
    })

if __name__ == '__main__':
    print("🚀 GENESIS PRODUCTION OS: Starting on port 5000...")
    app.run(host='0.0.0.0', port=5000)
