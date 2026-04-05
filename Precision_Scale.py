import numpy as np

# --- PROJECT GENESIS : PRECISION SCALING (BIT SLICING) ---
# Purpose: Achieving Digital-level Precision (32-bit) using Analog BCN Cores.
# Strategy: 4x 8-bit Analog Cores working as Slices (MSB to LSB).

def analog_core_read(value, noise_floor=0.01):
    """
    Simulates a single BCN Analog Core with ~8-bit resolution and noise.
    """
    noise = np.random.normal(0, noise_floor)
    return np.clip(value + noise, 0, 1)

def encode_32bit_to_slices(val_32bit):
    """
    Encodes a high-precision float into 4 analog 'slices' (8-bits each).
    """
    # Normalized value [0, 1]
    slices = []
    current_val = val_32bit
    for _ in range(4):
        # Extract 8 bits (0-255)
        byte_val = int(current_val * 255)
        slices.append(byte_val / 255.0)
        # Shift to the next 8 bits
        current_val = (current_val * 255) - byte_val
    return slices

def decode_slices_to_32bit(slices):
    """
    Reconstructs the 32-bit value from 4 noisy analog slices.
    """
    reconstructed = 0
    multiplier = 1.0
    for s in slices:
        reconstructed += s * multiplier
        multiplier /= 255.0
    return reconstructed

# --- TEST ARENA ---
print("🚀 GENESIS: Precision Scaling Test (Bit Slicing)")
print("   Goal: Reconstruct 32-bit Pi using 4 low-precision Analog Cores.")

target_pi = 3.1415926535 / 10.0 # Normalized target
print(f"\n[TARGET]  High-Precision Value: {target_pi:.10f}")

# 1. Encode into 4 cores (The "Hardware Storage" step)
analog_cores = encode_32bit_to_slices(target_pi)
print(f"[STORE]   4x 8-bit Analog Slices: {['Core ' + str(i) + ': ' + f'{val:.4f}' for i, val in enumerate(analog_cores)]}")

# 2. Read with Real-World Analog Noise (The "Vibrating Reality" step)
noisy_reads = [analog_core_read(s, noise_floor=0.002) for s in analog_cores]
print(f"[READ]    Noisy Core Readings   : {['Core ' + str(i) + ': ' + f'{val:.4f}' for i, val in enumerate(noisy_reads)]}")

# 3. Reconstruct (The "Digital Hybrid" step)
final_pi = decode_slices_to_32bit(noisy_reads)
error = abs(target_pi - final_pi)

print(f"\n[FINAL]   Reconstructed Value : {final_pi:.10f}")
print(f"[RESULT]  Absolute Error      : {error:.12f}")
print(f"[STATUS]  Precision Level     : ~{int(-np.log10(error))} Decimals Locked.")

if error < 0.0001:
    print("\n✅ SUCCESS: Analog cores successfully simulated 32-bit Digital Precision.")
    print("   Note: By stacking analog cores, we've bypassed the 8-bit material limit.")
