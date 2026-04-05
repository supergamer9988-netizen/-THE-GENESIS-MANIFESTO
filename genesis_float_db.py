import serial
import time
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances

# --- PROJECT GENESIS : HIGH-PRECISION FLOAT-DB (GENESIS-FPU) ---
# Goal: Store and retrieve Floating Point numbers with 5-decimal accuracy.
# Strategy: Coarse-Fine Encoding (Integer part vs Decimal part) + Differential Noise Reduction.

PORT = 'COM3' # Update!
BAUD = 115200

# Initialize Serial
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    print("✅ GENESIS Precision Database Linked.")
except:
    print("❌ Hardware Link Failed. Check COM Port.")
    exit()

db_storage = []

def send_to_chip(val_0_255):
    """Stimulate BCN Lattice and capture 5D vector."""
    ser.write(bytes([int(val_0_255)]))
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if "PRECISION:" in line:
                parts = line.split(":")[1].split(',')
                return np.array([int(p) for p in parts])

def encode_float_physical(number):
    """
    Encode an analog float (e.g., 3.14159) into a 5D Physical Vector.
    - COARSE: Integer (Cores 0-1)
    - FINE:   Decimal (Cores 2-4) Zoom-in trick
    """
    # 1. Split into Integer and Decimal parts
    integer_part = int(number)
    decimal_part = number - integer_part
    
    # 2. Coarse Encoding (Integer -> Voltage)
    # Range 0-100 -> 0-255 PWM
    val_int = np.clip(integer_part * 2.55, 0, 255)
    vec_int = send_to_chip(val_int)
    
    # 3. Fine Encoding (Decimal -> Voltage Zoom-in)
    # Range 0.0-0.99999 -> 0-255 PWM (Full scale zoom)
    val_dec = int(decimal_part * 255)
    vec_dec = send_to_chip(val_dec)
    
    # 4. Integrate Vectors (Hybrid Model)
    # Hybrid Vector = [Int_Core0, Int_Core1, Dec_Core2, Dec_Core3, Dec_Core4]
    hybrid_vec = np.concatenate([vec_int[0:2], vec_dec[2:5]])
    
    # 5. Differential Noise Cancellation
    # Subtract adjacent core noise
    clean_vec = np.diff(hybrid_vec)
    
    return clean_vec

def db_insert_float(key, number):
    print(f"🧬 Encoding {number:.5f} into BCN Lattice...", end='')
    vector = encode_float_physical(number)
    db_storage.append({
        "key": key,
        "val": number,
        "vec": vector
    })
    print(" ✅ Secured.")

def db_search_float(query_number):
    """Find the closest physical numeric match via Euclidean Distance."""
    print(f"\n🔍 Querying Physics for Value: {query_number:.5f}")
    query_vec = encode_float_physical(query_number)
    
    best_match = None
    min_dist = float('inf')
    
    for entry in db_storage:
        # Distance calculation
        dist = np.linalg.norm(query_vec - entry['vec'])
        print(f"-> Comparing to {entry['key']} ({entry['val']:.5f}) | Dist: {dist:.4f}")
        
        if dist < min_dist:
            min_dist = dist
            best_match = entry
            
    return best_match, min_dist

# --- INITIALIZING CONSTANTS ---
print("\n--- 1. LOADING SCIENTIFIC CONSTANTS ---")
db_insert_float("PI", 3.14159)
db_insert_float("EULER", 2.71828)
db_insert_float("PHI", 1.61803)
db_insert_float("USER_TARGET", 3.14000) # Near PI

# --- TESTING PRECISION ---
print("\n--- 2. PRECISION MATCHING TEST ---")
# Query 3.141 (Should be closer to PI than USER_TARGET)
result, dist = db_search_float(3.14100)

if result:
    print(f"\n✅ SUCCESS: Closest physical match is {result['key']} ({result['val']:.5f})")
    print(f"   Confidence Offset (Noise): {dist:.4f}")
else:
    print("❌ Match Failed.")

ser.close()
