import serial
import serial.tools.list_ports
import time
import json
import numpy as np
from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- PROJECT GENESIS : CLUSTER SERVER (cluster_server.py) ---
# Purpose: Auto-discover all GENESIS Blades, fuse into a high-dimensional AI cluster.
# Scale: N blades × 16 cores = N×16 output dimensions
# Endpoint: POST /embed  {"text": "Hello GENESIS"}

app = Flask(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
BAUD     = 115200
TIMEOUT  = 1
HANDSHAKE_CMD = b"V:0\n"    # Probe command to verify a GENESIS blade
GENESIS_RESPONSE_PREFIX = "DATA:"

class GenesisNode:
    """Represents one connected GENESIS Blade."""
    def __init__(self, port: str, ser: serial.Serial, node_id: int):
        self.port    = port
        self.ser     = ser
        self.node_id = node_id
        self.cores   = 16
        self.multipliers = np.ones(16)

        # Load per-board calibration if it exists
        cal_file = f"calibration_{port.replace('/', '_').replace('COM','COM')}.json"
        try:
            with open(cal_file) as f:
                cal = json.load(f)
                self.multipliers = np.array(cal['multipliers'])
                print(f"   📂 Calibration loaded for {port}")
        except FileNotFoundError:
            print(f"   ⚠️  No calibration for {port} — using raw values.")

    def query(self, stimulus: int) -> list:
        """Send V:stimulus → return calibrated 16D vector."""
        try:
            self.ser.reset_input_buffer()
            self.ser.write(f"V:{stimulus}\n".encode())
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()

            if line.startswith(GENESIS_RESPONSE_PREFIX):
                raw = np.array([int(x) for x in line.split(":")[1].split(',')])
                corrected  = np.clip(raw * self.multipliers, 0, 4095)
                normalized = corrected / 4095.0
                return normalized.tolist()
        except Exception as e:
            print(f"⚠️  Node {self.node_id} ({self.port}) error: {e}")

        return [0.0] * 16  # Dead-neuron fallback

    def close(self):
        self.ser.close()

# ── Auto-Discovery ────────────────────────────────────────────────────────────
def discover_blades() -> list:
    """Scan all COM ports and identify GENESIS Blades by handshake."""
    print("🔍 Scanning for GENESIS Blade nodes...")
    nodes   = []
    ports   = serial.tools.list_ports.comports()
    node_id = 0

    for p in ports:
        try:
            s = serial.Serial(p.device, BAUD, timeout=TIMEOUT)
            time.sleep(2)                       # Wait for ESP32 reset

            s.reset_input_buffer()
            s.write(HANDSHAKE_CMD)
            response = s.readline().decode('utf-8', errors='ignore').strip()

            if response.startswith(GENESIS_RESPONSE_PREFIX):
                node = GenesisNode(p.device, s, node_id)
                nodes.append(node)
                node_id += 1
                print(f"  ✅ Node-{node.node_id} detected on {p.device}")
            else:
                s.close()
                print(f"  ⏭️  {p.device} — not a GENESIS blade (response: '{response[:20]}...')")

        except Exception as e:
            print(f"  ✖️  {p.device} — skipped ({e})")

    return nodes

# ── Boot ──────────────────────────────────────────────────────────────────────
nodes = discover_blades()

if not nodes:
    print("\n⚠️  No hardware found — running in SIMULATION mode.")
    SIMULATION = True
    TOTAL_DIMS = 64  # Simulate 4 boards
else:
    SIMULATION = False
    TOTAL_DIMS = len(nodes) * 16

print(f"\n🚀 GENESIS CLUSTER ONLINE")
print(f"   Nodes      : {len(nodes)}")
print(f"   Total Cores: {TOTAL_DIMS}")
print(f"   Mode       : {'SIMULATION' if SIMULATION else 'HARDWARE'}")

# ── Parallel Query ────────────────────────────────────────────────────────────
def cluster_query(stimulus: int) -> list:
    """Query all nodes in parallel and merge into a super-vector."""
    if SIMULATION:
        # 4-board synthetic simulation
        super_vec = []
        for i in range(4):
            x = np.linspace(0, np.pi, 16) + (i * 0.4)
            v = np.sin(x + (stimulus / 255.0)) * 0.5 + 0.5
            super_vec.extend(v.tolist())
        return super_vec

    results = {}
    with ThreadPoolExecutor(max_workers=len(nodes)) as pool:
        future_map = {pool.submit(node.query, stimulus): node.node_id for node in nodes}
        for future in as_completed(future_map):
            nid = future_map[future]
            results[nid] = future.result()

    # Merge in node order
    super_vec = []
    for nid in sorted(results.keys()):
        super_vec.extend(results[nid])
    return super_vec

# ── API ────────────────────────────────────────────────────────────────────────
@app.route('/status')
def status():
    return jsonify({
        "system"     : "GENESIS-CLUSTER",
        "nodes"      : len(nodes),
        "total_cores": TOTAL_DIMS,
        "simulation" : SIMULATION,
        "node_ports" : [n.port for n in nodes]
    })

@app.route('/embed', methods=['POST'])
def embed():
    body = request.get_json(force=True)
    text = body.get('text', '')
    if not text:
        return jsonify({"error": "text field required"}), 400

    stimulus = sum(ord(c) for c in text) % 256
    vector   = cluster_query(stimulus)

    return jsonify({
        "text"    : text,
        "stimulus": stimulus,
        "vector"  : vector,
        "dim"     : len(vector),
        "nodes"   : len(nodes),
        "mode"    : "simulation" if SIMULATION else "hardware"
    })

@app.route('/similarity', methods=['POST'])
def similarity():
    body = request.get_json(force=True)
    a, b = body.get('a', ''), body.get('b', '')
    va = np.array(cluster_query(sum(ord(c) for c in a) % 256))
    vb = np.array(cluster_query(sum(ord(c) for c in b) % 256))
    score = float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb) + 1e-9))
    return jsonify({"a": a, "b": b, "similarity": round(score, 4), "dim": int(TOTAL_DIMS)})

# ── Shutdown hook ─────────────────────────────────────────────────────────────
import atexit
def cleanup():
    for n in nodes:
        n.close()
    print("🔌 All GENESIS nodes disconnected.")
atexit.register(cleanup)

if __name__ == '__main__':
    print("\n🌐 Cluster API running on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
