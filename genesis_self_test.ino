/*
 * PROJECT GENESIS : BLADE V1.0 - HARDWARE SELF-TEST FIRMWARE
 * Purpose: Factory QC (Quality Control) Check after Soldering.
 * Tests: 16-Core continuity, short detection, open circuit detection.
 * Expected: All 16 cores report [OK] for a healthy board.
 */

#include <Arduino.h>

// --- PIN DEFINITIONS (Match V1.0 Netlist) ---
#define PIN_DAC  25
#define PIN_ADC  36
#define S0       13
#define S1       12
#define S2       14
#define S3       27

// --- QC THRESHOLDS ---
#define DEAD_THRESHOLD    100   // Below this = Open Circuit (Broken clip/contact)
#define SHORT_THRESHOLD  3950   // Above this = Short Circuit (Bridged solder)

void setup() {
    Serial.begin(115200);
    
    pinMode(PIN_DAC, OUTPUT);
    pinMode(S0, OUTPUT); pinMode(S1, OUTPUT);
    pinMode(S2, OUTPUT); pinMode(S3, OUTPUT);
    
    // Full resolution for accurate QC
    analogReadResolution(12);        // 0-4095
    analogSetAttenuation(ADC_11db);  // Full 0-3.3V span
    
    Serial.println("====================================");
    Serial.println("  GENESIS BLADE V1.0 - SELF-TEST  ");
    Serial.println("====================================");
    Serial.println("{\"status\":\"SELF_TEST_START\"}");
}

void selectMux(int ch) {
    digitalWrite(S0, ch & 0x01);
    digitalWrite(S1, (ch >> 1) & 0x01);
    digitalWrite(S2, (ch >> 2) & 0x01);
    digitalWrite(S3, (ch >> 3) & 0x01);
    delayMicroseconds(20);
}

void loop() {
    // Drive at 50% (128) for a neutral QC stimulus
    dacWrite(PIN_DAC, 128);
    delay(15);
    
    Serial.println("--- SCANNING 16 CORES ---");
    
    int ok_count = 0;
    int dead_count = 0;
    int short_count = 0;
    
    for (int i = 0; i < 16; i++) {
        selectMux(i);
        
        // Oversample x5 for QC stability
        long acc = 0;
        for (int k = 0; k < 5; k++) { acc += analogRead(PIN_ADC); }
        int val = acc / 5;
        
        Serial.print("  Core-");
        if (i < 10) Serial.print("0"); // Zero-padding
        Serial.print(i); 
        Serial.print(": ");
        Serial.print(val);
        Serial.print("/4095  ");
        
        if (val < DEAD_THRESHOLD) {
            Serial.println("[DEAD / OPEN CIRCUIT]");
            dead_count++;
        } else if (val > SHORT_THRESHOLD) {
            Serial.println("[SHORT CIRCUIT]");
            short_count++;
        } else {
            Serial.println("[OK]");
            ok_count++;
        }
    }
    
    // Final QC Report
    Serial.println("--- QC REPORT ---");
    Serial.print("  PASS: "); Serial.println(ok_count);
    Serial.print("  DEAD: "); Serial.println(dead_count);
    Serial.print("  SHORT: "); Serial.println(short_count);
    
    if (ok_count == 16) {
        Serial.println(">>> BLADE STATUS: [PRODUCTION CERTIFIED] <<<");
    } else {
        Serial.println(">>> BLADE STATUS: [FAULT DETECTED - INSPECT] <<<");
    }
    
    Serial.println("=================================");
    delay(2000);
}
