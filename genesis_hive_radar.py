import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# --- GENESIS HIVE: REAL-TIME RADAR ANALYSIS (V 1.0) ---
# Purpose: Visualize the 5 unique "Personalities" of your BCN Cores.
# C1: Impulsive (Direct)
# C2: Normal (1k)
# C3: Rigor (10k)
# C4: High-Threshold (22k)
# C5: Hibernator (100k)

PORT = 'COM3' # Update!
BAUD = 115200

# Initialize Serial
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print("✅ GENESIS Hive Linked. Watching Synapses...")
except:
    print("❌ Connection Failed. Check Wiring/COM Port!")
    exit()

# Radar Plot Configuration
labels = ['Core 1 (Pulse)', 'Core 2 (Normal)', 'Core 3 (Rigor)', 'Core 4 (Cold)', 'Core 5 (Skeptical)']
num_vars = len(labels)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1] # Close the circle

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True), facecolor='#0B1120')

def update(frame):
    if ser.in_waiting:
        try:
            line = ser.readline().decode('utf-8').strip()
            if line.startswith("CLUSTER_DATA:"):
                # Data Parse: "CLUSTER_DATA:512,120,40,10,0"
                raw_str = line.split(":")[1]
                values = [int(v) for v in raw_str.split(',')]
                
                # Normalization (0-1023 -> 0.0-1.0)
                norm_values = [v/1023.0 for v in values]
                norm_values += norm_values[:1] # Close the circle

                ax.clear()
                ax.set_theta_offset(np.pi / 2)
                ax.set_theta_direction(-1)
                
                # Radar Geometry
                ax.plot(angles, norm_values, linewidth=2, linestyle='solid', color='#00d1ff')
                ax.fill(angles, norm_values, '#00d1ff', alpha=0.3)
                
                # Styling
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(labels, color='white', size=10)
                ax.set_ylim(0, 1)
                ax.set_yticklabels([]) # Clear numeric clutter
                ax.grid(color='rgba(255,255,255,0.1)')
                
                ax.set_title("GENESIS CLUSTER: 5-CORE ACTIVITY", color='white', pad=20, size=15)
                # Show raw numbers in subtitle
                plt.suptitle(f"RAW DATA: {raw_str}", color='#FFD700', y=0.08)

        except Exception as e:
            pass

ani = FuncAnimation(fig, update, interval=20)
plt.style.use('dark_background')
plt.show()
