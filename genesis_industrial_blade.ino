// PROJECT GENESIS : INDUSTRIAL BLADE V1.1 (SIGNAL INTEGRITY EDITION)
// Purpose: High-Fidelity 16-Core BCN Management via ESP32 + MCP6002 Op-Amp Buffer.
// Strategy: DAC Precise Driving + ADC Buffered Sensing + Star Grounding Logic.

const int dacPin = 25;  // DAC1 -> MCP6002 Buffer (+) -> BCN Common Input
const int readPin = 36; // BCN Mux Output -> MCP6002 Buffer (+) -> ESP32 VP (ADC1)

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
    
    // Industrial PIN Directions
    pinMode(s0, OUTPUT);
    pinMode(s1, OUTPUT);
    pinMode(s2, OUTPUT);
    pinMode(s3, OUTPUT);
    pinMode(readPin, INPUT);
    
    // ADC Calibration for ESP32 (Highly recommended for Industrial use)
    // analogReadResolution(12); // Standard is 12-bit (0-4095)
    
    // Stabilize Lattice Signal
    dacWrite(dacPin, 0); 
    
    Serial.println("✅ GENESIS Industrial Blade V1.1 - NOISE KILLER ACTIVE.");
    Serial.println("Hardware: ESP32 + MCP6002 Dual-Buffer Stage + 16x Fuse Clips.");
}

void loop() {
    if (Serial.available() > 0) {
        // Read input voltage level (0-255)
        int stimulus = Serial.read();
        
        // 1. High-Fidelity Driving (via Op-Amp Buffer)
        dacWrite(dacPin, stimulus);
        
        // 2. Thermal & Signal Stabilization Delay (Optimized for Wind Tunnel)
        delayMicroseconds(600); 
        
        // 3. Multi-Core Vector Harvest (16 Dimensions)
        Serial.print("BLADE_V1.1:");
        for (int i = 0; i < 16; i++) {
            selectMuxChannel(i);
            delayMicroseconds(80); // Mux Switch Settle (Buffered)
            
            // Read response from Buffered ADC Stage
            int val = analogRead(readPin);
            Serial.print(val);
            if (i < 15) Serial.print(",");
        }
        Serial.println();
        
        // Optional: Signal Decay Phase to maintain Lattice Lifespan
        // dacWrite(dacPin, 0);
    }
}
