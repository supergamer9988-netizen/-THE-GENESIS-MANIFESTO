import numpy as np
from functools import reduce

# --- PROJECT GENESIS : RAMANUJAN RNS ENGINE V1.0 ---
# Purpose: High-Precision Parallel Arithmetic via Residue Number System.
# Technique: Chinese Remainder Theorem (CRT) + GENESIS Core Mapping.

class Ramanujan_RNS:
    def __init__(self):
        # 1. Coprime Moduli Set (Must be relatively prime)
        # Using 9 cores for wide dynamic range.
        self.moduli = [3, 5, 7, 11, 13, 17, 19, 23, 29]
        self.M = reduce(lambda x, y: x * y, self.moduli) # Total Dynamic Range ≈ 6.46 Billion
        print(f"🌌 Ramanujan RNS Architecture Online.")
        print(f"   Moduli Cores   : {self.moduli}")
        print(f"   Dynamic Range : 0 to {self.M:,}")

    def encode(self, number):
        """Decimal -> RNS Vector (The 'Charge' sent to GENESIS Cores)"""
        if number >= self.M:
            raise ValueError(f"Number {number} exceeds dynamic range {self.M}")
        return [number % m for m in self.moduli]

    def decode(self, rns_vector):
        """RNS Vector -> Decimal (Chinese Remainder Theorem)"""
        result = 0
        for i, modulus in enumerate(self.moduli):
            ai = rns_vector[i]
            Mi = self.M // modulus
            # Modular Multiplicative Inverse (yi * Mi ≡ 1 mod modulus)
            yi = pow(Mi, -1, modulus) 
            result += ai * Mi * yi
        return result % self.M

    # --- Parallel Arithmetic (No Carry Chain!) ---

    def add(self, vec_a, vec_b):
        """Parallel Addition: Result[i] = (A[i] + B[i]) mod moduli[i]"""
        return [(a + b) % m for a, b, m in zip(vec_a, vec_b, self.moduli)]

    def mul(self, vec_a, vec_b):
        """Parallel Multiplication: Result[i] = (A[i] * B[i]) mod moduli[i]"""
        return [(a * b) % m for a, b, m in zip(vec_a, vec_b, self.moduli)]

# ─────────────────────────────────────────────────────────────────
# GENESIS HARDWARE SIMULATOR
# ─────────────────────────────────────────────────────────────────

def run_genesis_calculation(num1, num2, operation='mul'):
    engine = Ramanujan_RNS()
    
    print(f"\n🔢 Computation: {num1} {operation} {num2}")
    
    # 1. Encode into GENESIS Cores
    v1 = engine.encode(num1)
    v2 = engine.encode(num2)
    print(f"[STAGE 1] Encoded into {len(v1)} BCN Cores")
    
    # 2. Perform Parallel Compute (The Physical Magic)
    print(f"[STAGE 2] Performing High-Speed Carry-Free Calculation...")
    if operation == 'mul':
        res_vec = engine.mul(v1, v2)
        truth = num1 * num2
    else:
        res_vec = engine.add(v1, v2)
        truth = num1 + num2
        
    # 3. Decode back to Decimal
    final_val = engine.decode(res_vec)
    print(f"[STAGE 3] Reconstructing Result via CRT...")
    
    print(f"\n--- [ CALCULATION REPORT ] ---")
    print(f"GENESIS Result: {final_val:,}")
    print(f"Digital Truth : {truth:,}")
    
    if final_val == truth:
        print("🎉 SUCCESS: Analog-RNS Precision Match Found.")
    else:
        print("❌ ERROR: Dynamic Range Overflow.")

if __name__ == "__main__":
    # Test a massive multiplication that would normally take many cycles
    # But GENESIS RNS does it in 1 cycle on each core.
    run_genesis_calculation(987654, 1234, operation='mul')
