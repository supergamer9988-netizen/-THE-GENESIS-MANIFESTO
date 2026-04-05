// GENESIS NEURAL PROCESSOR FIRMWARE V1.0 - CLOSED LOOP COMPUTE
// Purpose: Hardware-based Non-linear Function Mapping (Sine to Cosine)
// Data Input: Pin 3 (PWM) -> Connected to 5-Core Input Bus
// Data Output: MUX SIG -> A0 (Scanned via S0-S3 on D4-D7)

const int DATA_IN_PIN = 3; 
const int MUX_SIG = A0; 
const int S0 = 4;
const int S1 = 5;
const int S2 = 6;
const int S3 = 7;

void setup() {
  Serial.begin(115200);
  pinMode(DATA_IN_PIN, OUTPUT);
  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  pinMode(S3, OUTPUT);
  
  // High-frequency PWM for clean BCN stimulation (Optional/Default)
  // TCCR2B = (TCCR2B & 0xF8) | 0x01; // Increase PWM freq to 31kHz if needed
}

void selectChannel(int channel) {
  digitalWrite(S0, channel & 1);
  digitalWrite(S1, (channel >> 1) & 1);
  digitalWrite(S2, (channel >> 2) & 1);
  digitalWrite(S3, (channel >> 3) & 1);
}

void loop() {
  if (Serial.available() > 0) {
    // 1. Capture Input Byte (0-255)
    int inputVal = Serial.read(); 
    
    // 2. Stimulate BCN Lattice
    analogWrite(DATA_IN_PIN, inputVal);
    
    // 3. Hardware Reaction Latency (Allow material to settle)
    delayMicroseconds(500); 
    
    // 4. Scrape the 5-Core Reservoir State
    Serial.print("DATA:");
    for (int i = 0; i < 5; i++) {
        selectChannel(i);
        delayMicroseconds(100); 
        int val = analogRead(muxSig);
        Serial.print(val);
        if (i < 4) Serial.print(",");
    }
    Serial.println(); // Frame end
  }
}
