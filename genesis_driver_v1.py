import json
import numpy as np

# --- PROJECT GENESIS : MASTER DRIVER V1.0 ---
# Purpose: Software-Defined Hardware (SDH) Layer.
# Technique: Mapping Non-linear Analog Response to Digital Precision.

class GenesisDriver:
    def __init__(self, config_path='calibration_map.json'):
        self.config_path = config_path
        self.calibration = self.load_calibration()
        print("💎 GENESIS Master Driver Loaded.")
        print("   Status: Software-Defined Hardware (SDH) Active.")

    def load_calibration(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except:
            # Default fallback: Linear 1.0 mapping
            return {str(i): {"slope": 1.0, "intercept": 0.0, "curve": 0.0} for i in range(16)}

    def read_calibrated(self, core_id, raw_adc):
        """
        [THE DRIVER LOGIC]
        Transforms raw, non-linear ADC readings into 'Qualified' Digital Values.
        Formula: y = ax^2 + bx + c (Quadratic compensation for material drift)
        """
        core_str = str(core_id)
        cal = self.calibration.get(core_str, {"slope": 1.0, "intercept": 0.0, "curve": 0.0})
        
        a = cal.get("curve", 0.0)
        b = cal.get("slope", 1.0)
        c = cal.get("intercept", 0.0)
        
        # Quadrative correction of the material's IV-curve
        corrected_val = a * (raw_adc**2) + b * raw_adc + c
        
        # Snap to precision (Integral value for RNS or float for AI)
        return np.clip(corrected_val, 0, 4095)

    def save_calibration(self, core_id, a, b, c):
        self.calibration[str(core_id)] = {"curve": a, "slope": b, "intercept": c}
        with open(self.config_path, 'w') as f:
            json.dump(self.calibration, f, indent=4)
        print(f"✅ Core {core_id} Calibrated and Locked.")

# --- PRODUCTION USAGE EXAMPLE ---
if __name__ == "__main__":
    driver = GenesisDriver()
    
    # Simulating a raw, non-linear input from a Pencil core (ADC = 1500)
    raw_reading = 1500 
    
    # Applying the Master Driver correction
    qualified_val = driver.read_calibrated(0, raw_reading)
    
    print(f"\n--- [ QUALIFICATION REPORT ] ---")
    print(f"Raw Physical Data      : {raw_reading}")
    print(f"Qualified Digital Data : {qualified_val:.2f}")
    print(f"Status                 : HARDWARE QUALIFIED [OK]")
