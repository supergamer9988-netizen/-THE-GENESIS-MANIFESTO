// GENESIS CLUSTER DRIVER V1.1 - RADAR SYNC
// Purpose: Multi-channel data harvesting for 5-Core Radar Visualization
// Hardware: CD74HC4067 MUX + 5x BCN Memristors (Weighted Inputs)

const int MUX_SIG = A0; 
const int S0 = 4;
const int S1 = 5;
const int S2 = 6;
const int S3 = 7;

void setup() {
  Serial.begin(115200);   // High-speed link
  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  pinMode(S3, OUTPUT);
}

void selectChannel(int channel) {
  digitalWrite(S0, channel & 1);
  digitalWrite(S1, (channel >> 1) & 1);
  digitalWrite(S2, (channel >> 2) & 1);
  digitalWrite(S3, (channel >> 3) & 1);
}

void loop() {
  // Protocol: "CLUSTER_DATA:v1,v2,v3,v4,v5"
  Serial.print("CLUSTER_DATA:");
  
  for (int i = 0; i < 5; i++) {
    selectChannel(i);
    delayMicroseconds(500); // Signal settling
    
    int val = analogRead(MUX_SIG);
    Serial.print(val);
    
    if (i < 4) Serial.print(","); 
  }
  
  Serial.println(); // Frame end
  
  // Frequency tuned for Matplotlib realtime plotter
  delay(20); 
}
