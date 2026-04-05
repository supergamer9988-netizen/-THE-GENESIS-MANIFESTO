/* 
 * PROJECT GENESIS : THE PENCIL CALCULATOR FIRMWARE V1.9
 * Purpose: Single-Core/Multi-Core RNS Arithmetic Prototype.
 * Hardware: 2-Channel Integrated DAC-ADC BCN Interface.
 */

#include <Arduino.h>

// DAC Pins (Source Voltage)
#define DAC_A 25
#define DAC_B 26

// ADC Pins (Drain Current Measurement)
#define ADC_A 34
#define ADC_B 35

void setup() {
  Serial.begin(115200);
  pinMode(DAC_A, OUTPUT);
  pinMode(DAC_B, OUTPUT);
  
  // High-Resolution 12-bit Analog Setup
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);
  
  dacWrite(DAC_A, 0);
  dacWrite(DAC_B, 0);
  
  Serial.println("{\"status\":\"PENCIL_CALC_ONLINE\", \"arch\":\"DUAL_CORE_RNS\"}");
}

// ─────────────────────────────────────────────────────────────────
// LOW-LEVEL COMMAND PARSER
// ─────────────────────────────────────────────────────────────────

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    // Command: WRITE:core_id:val [STAGING RAM MODE]
    if (cmd.startsWith("WRITE:")) {
      int firstColon = cmd.indexOf(':');
      int secondColon = cmd.lastIndexOf(':');
      int core = cmd.substring(firstColon + 1, secondColon).toInt();
      int val = cmd.substring(secondColon + 1).toInt();
      
      // We apply the 'Staging' voltage to set the resistance state
      if(core == 0) dacWrite(DAC_A, val);
      else dacWrite(DAC_B, val);
      
      Serial.println("{\"status\":\"MEM_WRITE_ACK\", \"core\":" + String(core) + "}");
    }
    
    // Command: COMPUTE:core_id:val [CPU COMPUTE MODE]
    else if (cmd.startsWith("COMPUTE:")) {
      int firstColon = cmd.indexOf(':');
      int secondColon = cmd.lastIndexOf(':');
      int core = cmd.substring(firstColon + 1, secondColon).toInt();
      int in_v = cmd.substring(secondColon + 1).toInt();
      
      // 1. Stimulation Pulse (The Computing Vector)
      if(core == 0) dacWrite(DAC_A, in_v);
      else dacWrite(DAC_B, in_v);
      
      delay(20); // Signal stabilization for physical lattice
      
      // 2. Measure Parallel Conductance Output (The Mathematical Result)
      int result = 0;
      if(core == 0) result = analogRead(ADC_A);
      else result = analogRead(ADC_B);
      
      Serial.print("RES:");
      Serial.println(result);
      
      // Clear DAC line after pulse to save power
      dacWrite(DAC_A, 0);
      dacWrite(DAC_B, 0);
    }
    
    // Command: TEST:val [CALIBRATION SWEEP MODE]
    else if (cmd.startsWith("TEST:")) {
      int val = cmd.substring(5).toInt();
      dacWrite(DAC_A, val);
      delay(5); // Fast settle
      Serial.println(analogRead(ADC_A));
      dacWrite(DAC_A, 0);
    }
    
    // Status Check
    else if (cmd == "STATUS") {
      Serial.println("{\"status\":\"READY\", \"A_RAW\":" + String(analogRead(ADC_A)) + ", \"B_RAW\":" + String(analogRead(ADC_B)) + "}");
    }
  }
}
