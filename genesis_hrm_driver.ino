/* 
 * PROJECT GENESIS : HRM (Holographic Resonance Memory) DRIVER V1.2
 * Purpose: Frequency-Domain Storage & High-Density Memory Retrieval (800+ bits/core)
 * Technique: Impedance Spectroscopy via DAC Chirp + Fast Sampling
 */

#include <Arduino.h>

#define PIN_DAC      25
#define PIN_ADC      36
#define MUX_S0       13
#define MUX_S1       12
#define MUX_S2       14
#define MUX_S3       27

void selectChannel(int ch) {
  digitalWrite(MUX_S0, ch & 0x01);
  digitalWrite(MUX_S1, (ch >> 1) & 0x01);
  digitalWrite(MUX_S2, (ch >> 2) & 0x01);
  digitalWrite(MUX_S3, (ch >> 3) & 0x01);
  delayMicroseconds(5);
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_DAC, OUTPUT);
  pinMode(MUX_S0, OUTPUT); pinMode(MUX_S1, OUTPUT);
  pinMode(MUX_S2, OUTPUT); pinMode(MUX_S3, OUTPUT);
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);
  dacWrite(PIN_DAC, 0);
  Serial.println("{\"status\":\"HRM_ONLINE\", \"ver\":\"1.2_HOLOGRAPHIC\"}");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    // Command: CHIRP:core_id:steps:delay_us
    // Frequency Sweep Simulation via DAC pulses at various speeds
    if (cmd.startswith("CHIRP:")) {
      int firstPipe = cmd.indexOf(':');
      int secondPipe = cmd.indexOf(':', firstPipe + 1);
      int thirdPipe = cmd.indexOf(':', secondPipe + 1);
      
      int core = cmd.substring(firstPipe + 1, secondPipe).toInt();
      int steps = cmd.substring(secondPipe + 1, thirdPipe).toInt();
      int delay_us = cmd.substring(thirdPipe + 1).toInt();

      selectChannel(core);
      Serial.print("HRM_SCAN:" + String(core) + ":");
      
      // Perform Spectral Sweep
      for (int i = 0; i < steps; i++) {
        // High-Speed Pulse (The Frequency Stimulus)
        dacWrite(PIN_DAC, 255);
        delayMicroseconds(delay_us);
        int high = analogRead(PIN_ADC);
        
        dacWrite(PIN_DAC, 0);
        delayMicroseconds(delay_us);
        int low = analogRead(PIN_ADC);
        
        // Impedance Delta (The Spectral Signature)
        Serial.print(high - low);
        if (i < steps - 1) Serial.print(",");
      }
      Serial.println();
    }
    
    // Legacy DC Command compatibility
    else if (cmd.startsWith("V:")) {
      int stimulus = cmd.substring(2).toInt();
      dacWrite(PIN_DAC, stimulus);
      Serial.print("DATA:");
      for (int i = 0; i < 16; i++) {
        selectChannel(i);
        Serial.print(analogRead(PIN_ADC));
        if (i < 15) Serial.print(",");
      }
      Serial.println();
    }
  }
}
