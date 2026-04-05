import serial
import numpy as np
import time
import threading
import keyboard  # Requires: pip install keyboard
import pyautogui # Requires: pip install pyautogui
import webbrowser
from sklearn.neighbors import KNeighborsClassifier

# --- PROJECT GENESIS : MULTI-MODAL SENSE (HIVE MACHINE LEARNING) ---
# Goal: Train the 5-Core BCN Cluster to recognize physical events.
# Core Logic: Using KNN to map 5D Hardware States to Human Intent.

PORT = 'COM3' # Update!
BAUD = 115200

# Initialize Model
model = KNeighborsClassifier(n_neighbors=3)
X_train = []
y_train = []
is_trained = False

# Action Map (Jervis Mode)
def trigger_action(label):
    if label == 1: # BREATH
        print("\n[ACTION] EXHALATION DETECTED: Opening Research Dashboard...")
        webbrowser.open("https://github.com/supergamer9988-netizen/-BCN-FJH")
    elif label == 2: # TAP
        print("\n[ACTION] KINETIC VIBRATION: Locking System Protection...")
        # pyautogui.hotkey('win', 'l') # Optional: Uncomment to actually lock Windows
        pass

# Initialize Serial
try:
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    print("✅ GENESIS Hive Linked. Sensors Warming Up...")
except:
    print("❌ Connection Error. Check COM Port.")
    exit()

print("\n--- [ TRAINING PROTOCOL ] ---")
print(" [Space] : Hold for IDLE (Neutral State)")
print(" [1]     : Hold for BREATH (Exhalation onto BCN)")
print(" [2]     : Hold for TAP (Table/PCB Vibration)")
print(" [T]     : EXECUTE TRAINING (Live AI Ignition)")
print(" [Q]     : EXIT GENESIS")
print("-----------------------------\n")

def main_loop():
    global X_train, y_train, is_trained
    
    last_action_time = 0
    
    while True:
        if ser.in_waiting:
            try:
                line = ser.readline().decode('utf-8').strip()
                if line.startswith("CLUSTER_DATA:"):
                    data = line.split(":")[1]
                    raw = [int(v) for v in data.split(',')]
                    features = [v/1023.0 for v in raw] # Normalize
                    
                    # --- DATA COLLECTION PHASE ---
                    if keyboard.is_pressed('space'):
                        X_train.append(features)
                        y_train.append(0)
                        print(f"\rCollecting: [IDLE]   | Samples: {len(y_train)}", end='')
                        
                    elif keyboard.is_pressed('1'):
                        X_train.append(features)
                        y_train.append(1)
                        print(f"\rCollecting: [BREATH] | Samples: {len(y_train)}", end='')
                        
                    elif keyboard.is_pressed('2'):
                        X_train.append(features)
                        y_train.append(2)
                        print(f"\rCollecting: [TAP]    | Samples: {len(y_train)}", end='')
                        
                    elif keyboard.is_pressed('t'):
                        if len(X_train) > 15:
                            print("\n🧠 SYNAPTIC MAPPING IN PROGRESS...")
                            model.fit(X_train, y_train)
                            is_trained = True
                            print("🚀 GENESIS BRAIN IS LIVE. PREDICTION MODE ACTIVE. RUN!")
                            time.sleep(1)
                        else:
                            print("\n⚠️ Insufficient Data. Collect more samples (Space/1/2).")

                    # --- LIVE INFERENCE PHASE ---
                    elif is_trained:
                        prediction = model.predict([features])[0]
                        probs = model.predict_proba([features])[0]
                        confidence = max(probs) * 100
                        
                        label_text = "..."
                        if prediction == 0: label_text = "⚪ IDLE"
                        elif prediction == 1: label_text = "💨 BREATH DETECTED"
                        elif prediction == 2: label_text = "🔨 KINETIC TAP DETECTED"
                        
                        # Trigger once per event with cooldown
                        if confidence > 90 and prediction != 0 and (time.time() - last_action_time > 3):
                            trigger_action(prediction)
                            last_action_time = time.time()
                            
                        print(f"\rBRAIN STATUS: {label_text} | Confidence: {confidence:.0f}% | Signal: {raw}", end='')
                        
                if keyboard.is_pressed('q'):
                    print("\nShutting down Genesis Sense.")
                    break
                    
            except Exception as e:
                pass

if __name__ == "__main__":
    main_loop()

