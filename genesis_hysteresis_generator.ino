// GENESIS: HYSTERESIS SIGNAL GENERATOR V1.2
// Purpose: Automate UP/DOWN sweep for Memristor Fingerprint detection.
// I/O Mapping: PWM Pin 3 (Input) -> BCN Core -> Analog Pin A0 (Output)

const int pwmPin = 3;  
const int readPin = A0; 

void setup() {
  Serial.begin(115200); 
  pinMode(pwmPin, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    
    if (cmd == 'S') { // Command: START SCAN
      
      // 1. CLIMB (UP SWEEP): Increasing Stimulus (Memory Loading)
      for (int i = 0; i <= 255; i += 5) {
        analogWrite(pwmPin, i);
        delay(5); // Thermal Inertia Settle
        int val = analogRead(readPin);
        
        Serial.print(i); 
        Serial.print(",");
        Serial.println(val); 
      }

      // 2. FALL (DOWN SWEEP): Decreasing Stimulus (Memory Decay)
      for (int i = 255; i >= 0; i -= 5) {
        analogWrite(pwmPin, i);
        delay(5); 
        int val = analogRead(readPin);
        
        Serial.print(i);
        Serial.print(",");
        Serial.println(val);
      }
      
      Serial.println("END"); // Frame termination
      analogWrite(pwmPin, 0); // Cool down
    }
  }
}
