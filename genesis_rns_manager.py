import serial
import time
import numpy as np

# --- PROJECT GENESIS : RNS PARALLEL ENGINE (RESIDUE NUMBER SYSTEM) ---
# Goal: Perform carry-free parallel arithmetic using RNS on 5 BCN Cores.
# Logic: X -> (r1, r2, r3, r4, r5) via coprimes -> BCN Lattice Verification -> CRT Reconstruction.

PORT = 'COM3' # Update!
BAUD = 115200

# 1. RNS MODULI SETUP (Coprime Set)
# Range: 7 * 11 * 13 * 17 * 19 = 323,323 (Max representable integer)
MODULI = [7, 11, 13, 17, 19]

def rns_encode(X):
    """Convert Integer to Residues."""
    return [X % m for m in MODULI]

def chinese_remainder_theorem(residues):
    """Reconstruct Original Number from Residues via CRT."""
    def extended_gcd(a, b):
        if a == 0: return b, 0, 1
        d, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return d, x, y

    def modInverse(a, m):
        d, x, y = extended_gcd(a, m)
        if d != 1: raise Exception('Modular inverse does not exist')
        return (x % m + m) % m

    M = np.prod(MODULI)
    X = 0
    for r, m in zip(residues, MODULI):
        Mi = M // m
        yi = modInverse(Mi, m)
        X += r * Mi * yi
    return X % M

# Initialize Serial
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)
    print("✅ GENESIS RNS Engine Active. Coprime Parallelism Enabled.")
except:
    print("❌ Serial Error.")
    exit()

def process_rns_hardware(residues):
    """
    Inject each residue into its specific BCN Core.
    Core 1 = mod 7, Core 2 = mod 11, etc.
    """
    print(f"Injecting Residues {residues} into Physical Cores...")
    
    # We send a packet: [r1, r2, r3, r4, r5]
    ser.write(bytes(residues))
    
    h_residues = []
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if "RNS_DATA:" in line:
                parts = line.split(":")[1].split(',')
                # Read hardware-stabilized values
                h_readings = [int(p) for p in parts]
                
                # Reverse-map Analog back to Residue (Simple Calibration)
                # In real scenario, this uses the Hysteresis fingerprint
                for i, val in enumerate(h_readings):
                    # For demo: map analog range back to residue domain
                    h_residues.append(int((val / 1023) * MODULI[i]))
                break
    return h_residues

# --- RNS TEST OPERATION ---
TARGET_NUM = 12345
print(f"\n--- [ THE RNS CHALLENGE ] ---")
print(f"Goal: Store and Reconstruct {TARGET_NUM} using Material Residues.")

# 1. Digital Encoding
residues = rns_encode(TARGET_NUM)
print(f"1. RNS Residues: {residues}")

# 2. Physical Processing (Parallel Carry-Free Storage)
hw_residues = process_rns_hardware(residues)
print(f"2. BCN Material Residues: {hw_residues}")

# 3. Final Reconstruction
reconstructed = chinese_remainder_theorem(hw_residues)
print(f"3. CRT Reconstruction: {reconstructed}")

if reconstructed == TARGET_NUM:
    print("\n🏆 SUCCESS: BCN RNS RECONSTRUCTION PERFECT.")
else:
    print(f"\n⚠️ ERROR: Reconstruction Mismatch. (Offset: {abs(TARGET_NUM - reconstructed)})")

ser.close()
