// PROJECT GENESIS : HIGH-PRECISION DIFFERENTIAL DRIVER V1.5
// Purpose: Enable Floating-Point Precision on BCN Lattice via Coarse-Fine Muxing.
// Logic: Fast-sampling with differential noise cancellation.

const int dataPin = 3; // PWM Stimulus
const int readPin = A0; // Analog Response (from Mux)

// Multiplexer Selection Pins (CD74HC4067)
const int s0 = 8;
const int s1 = 9;
const int s2 = 10;
const int s3 = 11;

void selectMuxChannel(int channel) {
    digitalWrite(s0, channel & 0x01);
    digitalWrite(s1, channel & 0x02);
    digitalWrite(s2, channel & 0x04);
    digitalWrite(s3, channel & 0x08);
}

void setup() {
    Serial.begin(115200);
    pinMode(dataPin, OUTPUT);
    pinMode(s0, OUTPUT);
    pinMode(s1, OUTPUT);
    pinMode(s2, OUTPUT);
    pinMode(s3, OUTPUT);
    
    // Stabilize Lattice
    analogWrite(dataPin, 0);
    Serial.println("✅ GENESIS Precision FPU Ready.");
}

void loop() {
    if (Serial.available() > 0) {
        // Read target voltage (0-255)
        int stimulus = Serial.read();
        
        // 1. Inject Stimulus
        analogWrite(dataPin, stimulus);
        
        // 2. High-Speed Stabilization Delay
        delayMicroseconds(800); 
        
        // 3. Differential Multi-Core Sampling
        Serial.print("PRECISION:");
        for (int i = 0; i < 5; i++) {
            selectMuxChannel(i);
            delayMicroseconds(50); // Mux Switch Settle
            
            // Sample and send raw integer
            int val = analogRead(readPin);
            Serial.print(val);
            if (i < 4) Serial.print(",");
        }
        Serial.println();
        
        // Cool down slightly for thermal linearity
        // analogWrite(dataPin, 0); // Optional: Keep on for "Memory" effect
    }
}
