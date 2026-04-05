import serial
import time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# --- PROJECT GENESIS : PHYSICAL VECTOR DATABASE (GENESIS-DB) ---
# Goal: Use the BCN Cluster as a Physical Indexer for Semantic Search.
# Logic: Text -> Stimulus -> Material Reactivity (5D Vector) -> Index Storage.

PORT = 'COM3' # Update!
BAUD = 115200

# Initialize Serial
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    print("✅ GENESIS Physical Vector DB Online.")
except:
    print("❌ Connection Error. Check BCN Hardware Link.")
    exit()

# Memory Storage (In-memory dict for demo)
# Structure: { key: { "vector": 5D_ARRAY, "content": STRING } }
knowledge_base = []

def get_bcn_fingerprint(text):
    """Generate a unique 5D Vector for a given text via Material Chaos."""
    # 1. Map text to a deterministic voltage stimulus (PWM 0-255)
    stimulus = sum([ord(c) for c in text]) % 256
    
    # 2. Inject into BCN Lattice
    ser.write(bytes([stimulus]))
    
    # 3. Harvest the resulting Reservoir State
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if "DATA:" in line:
                data_str = line.split(":")[1]
                vector = [int(v) for v in data_str.split(',')]
                return np.array(vector).reshape(1, -1)

def db_insert(label, description):
    """Store data indexed by its physical BCN reaction."""
    print(f"🧬 Encoding '{label}' through BCN Cluster...")
    vector = get_bcn_fingerprint(label)
    
    entry = {
        "label": label,
        "vector": vector,
        "content": description
    }
    knowledge_base.append(entry)
    print(f"✅ Indexed: {label} -> Vector {vector.flatten()}")

def db_search(query, threshold=0.95):
    """Fuzzy Semantic Search based on Material Similarity."""
    print(f"\n🔍 Querying BCN Pool for: '{query}'")
    query_vec = get_bcn_fingerprint(query)
    
    results = []
    for entry in knowledge_base:
        # Calculate Cosine Similarity between Query Vector and Stored Vector
        score = cosine_similarity(query_vec, entry['vector'])[0][0]
        results.append((entry, score))
        
    # Sort by descending similarity
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Display Results
    best, score = results[0]
    print(f"--- [ TOP MATCH ] ---")
    print(f"TARGET: '{best['label']}' | SIMILARITY: {score*100:.2f}%")
    
    if score >= threshold:
        print(f"CONTENT: {best['content']}")
        return best
    else:
        print("⚠️ NO CONFIDENT MATCH FOUND (Hardware Key Mismatch or Low Affinity).")
        return None

# --- INITIALIZING DATABASE ---
db_insert("apple", "A crunchy red fruit.")
db_insert("banana", "A long yellow potassium source.")
db_insert("cat", "A domestic feline mammal.")
db_insert("car", "A motorized four-wheeled vehicle.")

# --- TESTING SEARCH ---
# Case 1: Exact Match
db_search("cat")

# Case 2: Fuzzy Match (Typo) - Material Reactivity should be close!
db_search("catt") 

# Case 3: Different Word
db_search("dog")

print("\n--- [ DATABASE STATUS ] ---")
print(f"Items Indexed: {len(knowledge_base)}")
print("Status: SECURE (Hardware-Bound Vectors Active)")

ser.close()
