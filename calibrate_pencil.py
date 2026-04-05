import serial
import time
import matplotlib.pyplot as plt

# --- PROJECT GENESIS : CORE CALIBRATION & BEHAVIOR ANALYSIS ---
# Purpose: Map the I-V curve of the pencil lead to find a linear computing range.

PORT = 'COM3' # Update to your COM Port
BAUD = 115200

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    print("✅ GENESIS Calibration Link Active.")
except:
    print("⚠️ Hardware offline. Check COM Port.")
    exit()

def run_calibration_sweep():
    print("🚀 Starting Voltage Sweep (DAC 0-255)...")
    input_vals = []
    output_vals = []

    # Sweep from 0 to 255 in steps of 5 for higher resolution
    for v in range(0, 256, 5):
        ser.write(f"TEST:{v}\n".encode())
        try:
            line = ser.readline().decode().strip()
            if line:
                res = int(line)
                input_vals.append(v)
                output_vals.append(res)
                print(f"   DAC: {v} -> ADC: {res}", end='\r')
        except:
            continue

    print("\n✅ Sweep Complete.")
    ser.close()

    # --- Analysis & Visualization ---
    plt.style.use('dark_background')
    plt.figure(figsize=(10, 6))
    plt.plot(input_vals, output_vals, marker='o', color='#00ff41', markersize=3, alpha=0.8)
    
    # Draw an ideal line for comparison
    ideal_x = [min(input_vals), max(input_vals)]
    ideal_y = [min(output_vals), max(output_vals)]
    plt.plot(ideal_x, ideal_y, '--', color='white', alpha=0.5, label='Ideal Linear Path')

    plt.title("GENESIS BCN-Core Transfer Characteristic", fontsize=14, color='#00ff41')
    plt.xlabel("Input DAC (Stimulus Voltage)", fontsize=12)
    plt.ylabel("Output ADC (Resultant Conductance)", fontsize=12)
    plt.grid(True, which='both', linestyle='--', alpha=0.3)
    plt.legend()
    
    print("\n📈 [Calibration Insight]")
    if len(output_vals) > 0:
        linearity = np.corrcoef(input_vals, output_vals)[0,1]
        print(f"   Correlation to Linear: {linearity:.4f}")
        if linearity > 0.98:
            print("   >>> GOLDEN CORE: Material is highly linear. Precision 100% likely.")
        elif linearity > 0.90:
            print("   >>> STABLE CORE: Some curvature detected. Calculator needs lookup table.")
        else:
            print("   >>> CHAOTIC CORE: Highly non-linear. Best for Reservoir Computing (AI).")
    
    plt.show()

if __name__ == "__main__":
    import numpy as np # Need for correlation
    run_calibration_sweep()
