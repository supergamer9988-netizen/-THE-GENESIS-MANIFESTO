// PROJECT GENESIS : BLADE V1.0 - 16-CORE ESP32 DRIVER
// Purpose: Manage 16 BCN Cores using Fuse-Clip Socket Architecture.
// Logic: Receives a stimulus, uses CD74HC4067 Multiplexer (16-channel)
// to sample responses, and sends a complete 16D vector back via Serial.

const int dataPin = 25; // DAC1 Output on ESP32 (Precise Analog Stimulus)
const int readPin = 36; // VP (GPIO36) Analog Input (ADC1)

// CD74HC4067 Multiplexer Selection Pins
const int s0 = 13;
const int s1 = 12;
const int s2 = 14;
const int s3 = 27;

void selectMuxChannel(int channel) {
    digitalWrite(s0, channel & 0x01);
    digitalWrite(s1, channel & 0x02);
    digitalWrite(s2, channel & 0x04);
    digitalWrite(s3, channel & 0x08);
}

void setup() {
    Serial.begin(115200);
    pinMode(s0, OUTPUT);
    pinMode(s1, OUTPUT);
    pinMode(s2, OUTPUT);
    pinMode(s3, OUTPUT);
    
    // Stabilize Lattice
    dacWrite(dataPin, 0); 
    Serial.println("✅ GENESIS Blade V1.0 Driver Online (ESP32 16-Core).");
}

void loop() {
    if (Serial.available() > 0) {
        // Read input value (0-255 mapped text)
        int val = Serial.read();
        
        // 1. Inject Stimulus into BCN Lattice
        dacWrite(dataPin, val);
        
        // 2. Short stabilization delay
        delayMicroseconds(500); 
        
        // 3. Sequential 16-Core Vector Harvest
        Serial.print("BLADE:");
        for (int i = 0; i < 16; i++) {
            selectMuxChannel(i);
            delayMicroseconds(50); // Mux Switch Settle
            
            // Read response
            int response = analogRead(readPin);
            Serial.print(response);
            if (i < 15) Serial.print(",");
        }
        Serial.println();
        
        // Slightly discharge to prevent polarization saturation
        // dacWrite(dataPin, 0); 
    }
}
