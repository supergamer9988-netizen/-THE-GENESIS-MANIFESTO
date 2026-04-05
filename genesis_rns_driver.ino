// PROJECT GENESIS : RNS PARALLEL DRIVER V2.0
// Purpose: Manage 5-Core BCN Residues via Modular Arithmetic.
// Logic: Receives 5 residues (8-bit) and maps them to PWM Output.
// Reads 5 stabilized response values (10-bit).

const int s0 = 8;
const int s1 = 9;
const int s2 = 10;
const int s3 = 11;
const int dataPin = 3; // PWM Output to Lattice
const int readPin = A0; // Analog Input from Mux

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
    
    Serial.println("✅ GENESIS RNS Parallel Driver V2.0 Online.");
}

void loop() {
    if (Serial.available() >= 5) {
        // Read 5-core Residue Packet
        int residues[5];
        for (int i = 0; i < 5; i++) {
            residues[i] = Serial.read();
        }
        
        // Stabilize Residues on Lattice (Serial Processing to Hardware Parallelism)
        int responses[5];
        for (int i = 0; i < 5; i++) {
            // Target specific core dynamic
            selectMuxChannel(i);
            delayMicroseconds(50);
            
            // Map 0-max_residue to PWM
            // For simplicity, we use the value relative to the coprime moduli in Python.
            analogWrite(dataPin, map(residues[i], 0, 20, 0, 255));
            delay(1); // Wait for material reaction
            
            responses[i] = analogRead(readPin);
        }
        
        // Send hardware-stabilized packet back to CRT Solver
        Serial.print("RNS_DATA:");
        for (int i = 0; i < 5; i++) {
            Serial.print(responses[i]);
            if (i < 4) Serial.print(",");
        }
        Serial.println();
    }
}
