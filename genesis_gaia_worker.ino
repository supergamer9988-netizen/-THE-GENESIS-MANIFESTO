// PROJECT GAIA : DISTRIBUTED WORKER NODE (I2C SLAVE V1.0)
// Purpose: Scalable Neural Processor for GAIA-Rack Architecture.
// Logic: Receives a vector chunk via I2C Bus, stimulates BCN Lattice, returns response.

#include <Wire.h>

// --- CONFIG ---
#define NODE_ID 1      // CHANGE THIS FOR EACH BOARD (2, 3, 4...)
#define GENESIS_PIN 3  // PWM Input to BCN
#define READ_PIN A0    // Analog response from BCN

volatile int lastPhysicalState = 0;

void setup() {
    Wire.begin(NODE_ID);           // Join I2C Bus as Slave
    Wire.onReceive(receiveCommand); // Handler for incoming vector data
    Wire.onRequest(sendResponse);   // Handler for Master's request for results
    
    pinMode(GENESIS_PIN, OUTPUT);
    // Note: Mux selection is implicit here; simplified for single-core-per-slave scale.
}

void loop() {
    // Slave is reactive; processing happens in ISR for lowest latency.
}

// Master sends a Vector Chunk (e.g., 32 samples of a huge signal)
void receiveCommand(int byteCount) {
    while (Wire.available()) {
        int stimulus = Wire.read(); // 0-255 mapped value
        
        // Rapid Physical Computing Cycle
        analogWrite(GENESIS_PIN, stimulus);
        delayMicroseconds(200); // Ultrashort Lattice stabilization
        
        // Capture specific material state at this temporal point
        lastPhysicalState = analogRead(READ_PIN);
    }
}

// Master requests the computed "Physical Embedding"
void sendResponse() {
    // Send 10-bit integer as 2 bytes
    byte buffer[2];
    buffer[0] = lastPhysicalState >> 8;
    buffer[1] = lastPhysicalState & 0xFF;
    Wire.write(buffer, 2);
}
