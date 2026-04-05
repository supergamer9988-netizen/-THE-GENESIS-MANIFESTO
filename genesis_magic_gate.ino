/* 
 * PROJECT GENESIS : MAGIC LOGIC GATE (In-Memory Compute) V1.5
 * Hardware Profile: GENESIS Blade (16-Core Crossbar)
 * Strategy: Memristor Aided LoGIC (MAGIC) - NOR operation.
 * 
 * Logic NOR (A, B) -> Store in Result Core
 * Truth Table:
 * A=0, B=0 -> Res=1
 * A=1, B=0 -> Res=0
 * A=0, B=1 -> Res=0
 * A=1, B=1 -> Res=0
 */

#include <Arduino.h>

#define PIN_DAC      25
#define PIN_ADC      36
#define MUX_S0       13
#define MUX_S1       12
#define MUX_S2       14
#define MUX_S3       27

// Thresholds for high/low resistance (calibrated to material)
const int STATE_THRESHOLD = 2000; 

void selectChannel(int ch) {
  digitalWrite(MUX_S0, ch & 0x01);
  digitalWrite(MUX_S1, (ch >> 1) & 0x01);
  digitalWrite(MUX_S2, (ch >> 2) & 0x01);
  digitalWrite(MUX_S3, (ch >> 3) & 0x01);
  delayMicroseconds(5);
}

int readState(int core) {
  selectChannel(core);
  dacWrite(PIN_DAC, 128); // Low voltage read
  delayMicroseconds(50);
  return analogRead(PIN_ADC);
}

void writeState(int core, bool high) {
  selectChannel(core);
  // High state = SET (Strong Pulse), Low state = RESET (No Pulse / Neutral)
  dacWrite(PIN_DAC, high ? 255 : 0); 
  delayMicroseconds(2000); // Pulse duration for material state change
  dacWrite(PIN_DAC, 0);
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_DAC, OUTPUT);
  pinMode(MUX_S0, OUTPUT); pinMode(MUX_S1, OUTPUT);
  pinMode(MUX_S2, OUTPUT); pinMode(MUX_S3, OUTPUT);
  analogReadResolution(12);
  
  Serial.println("{\"status\":\"MAGIC_LOGIC_ONLINE\", \"arch\":\"3D_CROSSBAR_V1\"}");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    // Command: MAGIC_NOR:inA:inB:outC
    if (cmd.startsWith("MAGIC_NOR:")) {
      int firstPipe = cmd.indexOf(':');
      int secondPipe = cmd.indexOf(':', firstPipe + 1);
      int thirdPipe = cmd.indexOf(':', secondPipe + 1);
      
      int coreA = cmd.substring(firstPipe + 1, secondPipe).toInt();
      int coreB = cmd.substring(secondPipe + 1, thirdPipe).toInt();
      int coreC = cmd.substring(thirdPipe + 1).toInt();

      Serial.println("{\"action\":\"COMPUTING_NOR\", \"A\":" + String(coreA) + ", \"B\":" + String(coreB) + "}");

      // 1. Read input states
      int valA = readState(coreA);
      int valB = readState(coreB);
      
      bool stateA = valA > STATE_THRESHOLD;
      bool stateB = valB > STATE_THRESHOLD;

      // 2. Perform In-Memory Logic (NOR)
      bool result = !(stateA || stateB);

      // 3. Write purely to target core (The Compute-in-Place step)
      writeState(coreC, result);

      Serial.print("RESULT:");
      Serial.print(result ? "1" : "0");
      Serial.print("|CORE_C_VAL:");
      Serial.println(readState(coreC));
    }
  }
}
