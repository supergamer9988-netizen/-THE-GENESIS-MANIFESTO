import serial
import time
import numpy as np
from sklearn.linear_model import LogisticRegression

# --- PROJECT GENESIS : THE POET (PHYSICAL NANO-LLM) ---
# Goal: Perform Next-Token Prediction using BCN Material Context.
# Strategy: Character Embedding -> BCN Reservoir (Memory) -> Logistic Readout.

PORT = 'COM3' # Update!
BAUD = 115200
SEQ_LENGTH = 5 # Context Window (Lookback)

# 1. PREPARE TRAINING DATA
text_corpus = "hello world genesis is alive ai is future " * 5
chars = sorted(list(set(text_corpus)))
char_to_int = {c: i for i, c in enumerate(chars)}
int_to_char = {i: c for i, c in enumerate(chars)}
vocab_size = len(chars)

def encode_pwm(char):
    idx = char_to_int[char]
    return int((idx / (vocab_size - 1)) * 255)

# Initialize Serial
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    print("✅ GENESIS Poet Linked. Loading Neural Weights...")
except:
    print("❌ Hardware Link Failed. Check COM Port.")
    exit()

# 2. DATA HARVESTING (Inject Text -> Record Material Reactions)
X_train = []
y_train = []

print(f"Feeding corpus to BCN Lattice... (Length: {len(text_corpus)} chars)")

for i in range(len(text_corpus) - 1):
    current_char = text_corpus[i]
    next_char = text_corpus[i+1]
    
    # Send Token Stimulus (PWM)
    ser.write(bytes([encode_pwm(current_char)]))
    
    # Capture State
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if "DATA:" in line:
                data_str = line.split(":")[1]
                vector = [int(v) for v in data_str.split(',')]
                X_train.append(vector)
                y_train.append(char_to_int[next_char])
                break

# 3. TRAINING THE READOUT (Softmax Layer Emulator)
print("Training Semantic Readout (Logistic Regression)...")
model = LogisticRegression(max_iter=2000, multi_class='multinomial')
model.fit(X_train, y_train)

# 4. GENERATIVE MODE (GENESIS Speaking)
print("\n--- [ 🤖 GENESIS AI SPOKE ] ---")
seed = "hello"
print(f"SEED: {seed}", end='', flush=True)

input_char = seed[-1]
for _ in range(30):
    # 1. Stimulate with latest char
    ser.write(bytes([encode_pwm(input_char)]))
    
    # 2. Get Material Context
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if "DATA:" in line:
                state = [int(v) for v in line.split(":")[1].split(',')]
                
                # 3. Predict Next Token from Material State
                pred_idx = model.predict([state])[0]
                next_char = int_to_char[pred_idx]
                
                print(next_char, end='', flush=True)
                input_char = next_char
                break
    time.sleep(0.05)

print("\n--- [ GENERATION COMPLETE ] ---")
ser.close()
