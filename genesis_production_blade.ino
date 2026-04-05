/* 
 * PROJECT GENESIS : PRODUCTION BLADE FIRMWARE V1.0
 * Hardware Profile: ESP32-WROOM + MCP6002 Dual-Buffer + 16x Fuse Clips
 * Purpose: Scalable 16-Core Physical Vectorization Engine.
 * Communication: Serial @ 115200bps (JSON / Data Stream)
 */

#include <Arduino.h>

// --- PIN DEFINITIONS (MATCHING MASTER NETLIST) ---
#define PIN_DAC      25  // Input to Chips via MCP6002 Buffer 1
#define PIN_ADC      36  // Output from Mux via MCP6002 Buffer 2 (VP)
#define MUX_S0       13
#define MUX_S1       12
#define MUX_S2       14
#define MUX_S3       27

// --- GLOBAL CONFIG ---
const int CORES = 16;
const int OVERSAMPLING = 10; // Read 10 times and average to kill thermal noise

void setup() {
  Serial.begin(115200);
  
  // Power-On Signal Integrity Check
  pinMode(PIN_DAC, OUTPUT);
  pinMode(MUX_S0, OUTPUT); pinMode(MUX_S1, OUTPUT);
  pinMode(MUX_S2, OUTPUT); pinMode(MUX_S3, OUTPUT);
  
  // High-Resolution Analog Setup
  analogReadResolution(12);       // 0-4095 range
  analogSetAttenuation(ADC_11db); // Full range 0.0V - 3.3V
  
  // Initialize Lattice to Zero
  dacWrite(PIN_DAC, 0);
  
  Serial.println("{\"status\":\"BOOT_SUCCESS\", \"device\":\"GENESIS_BLADE_PROD_V1\", \"cores\":16}");
}

// Fast Multiplexer Channel Selection
void selectChannel(int ch) {
  digitalWrite(MUX_S0, ch & 0x01);
  digitalWrite(MUX_S1, (ch >> 1) & 0x01);
  digitalWrite(MUX_S2, (ch >> 2) & 0x01);
  digitalWrite(MUX_S3, (ch >> 3) & 0x01);
  delayMicroseconds(10); // Switching stabilization
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    // Command: V:128 (Trigger 16-Core Vectorization)
    if (cmd.startsWith("V:")) {
      int stimulus = cmd.substring(2).toInt();
      
      // 1. Precise Analog Drive
      dacWrite(PIN_DAC, stimulus);
      delayMicroseconds(800); // Lattice reaction window
      
      // 2. High-Speed 16-Core Scan
      Serial.print("DATA:");
      for (int i = 0; i < CORES; i++) {
        selectChannel(i);
        
        // Signal Averaging for Noise Kill
        long accumulator = 0;
        for (int k = 0; k < OVERSAMPLING; k++) {
          accumulator += analogRead(PIN_ADC);
        }
        int averaged_val = accumulator / OVERSAMPLING;
        
        Serial.print(averaged_val);
        if (i < CORES - 1) Serial.print(",");
      }
      Serial.println();
    }
    
    // Mode: CALIBRATE (Pre-heat the Lattice for thermal stability)
    else if (cmd == "CALIBRATE") {
      dacWrite(PIN_DAC, 255);
      Serial.println("{\"status\":\"THERMAL_PREHEAT_ACTIVE\"}");
    }
    
    // Mode: SLEEP (Energy save)
    else if (cmd == "SLEEP") {
      dacWrite(PIN_DAC, 0);
      Serial.println("{\"status\":\"STANDBY\"}");
    }
  }
}
