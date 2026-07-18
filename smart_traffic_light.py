const int sensorPins[4] = {2, 3, 4, 5};     
const int redPins[4]    = {6, 9, A0, A3};   
const int yellowPins[4] = {7, 10, A1, A4};  
const int greenPins[4]  = {8, 11, A2, A5};  

const int buzzerPin = 12; 

int activeLane = 0; 
const unsigned long minGreenTime = 4000; 

void setup() {
  Serial.begin(9600);
  Serial.println("--- Smart Traffic Light System Initialized ---");

  for (int i = 0; i < 4; i++) {
    pinMode(sensorPins[i], INPUT);
    pinMode(redPins[i], OUTPUT);
    pinMode(yellowPins[i], OUTPUT);
    pinMode(greenPins[i], OUTPUT);
    
    digitalWrite(redPins[i], HIGH);
    digitalWrite(yellowPins[i], LOW);
    digitalWrite(greenPins[i], LOW);
  }
  
  pinMode(buzzerPin, OUTPUT);

  digitalWrite(redPins[activeLane], LOW);
  digitalWrite(greenPins[activeLane], HIGH);
  Serial.println("Lane 1 is initially ACTIVE.");
}

void loop() {
  for (int i = 0; i < 4; i++) {
    if (i == activeLane) {
      continue;
    }

    int vehicleDetected = digitalRead(sensorPins[i]);

    if (vehicleDetected == HIGH) {
      Serial.print("Vehicle detected on inactive Lane ");
      Serial.println(i + 1);
      
      switchLanes(activeLane, i);
      
      delay(minGreenTime);
      break; 
    }
  }
}

void switchLanes(int current, int next) {
  Serial.print("Transitioning priority from Lane ");
  Serial.print(current + 1);
  Serial.print(" to Lane ");
  Serial.println(next + 1);

  digitalWrite(greenPins[current], LOW);
  digitalWrite(yellowPins[current], HIGH);

  for (int b = 0; b < 3; b++) {
    tone(buzzerPin, 1000, 200); 
    delay(400);                
  }
  delay(800); 

  digitalWrite(yellowPins[current], LOW);
  digitalWrite(redPins[current], HIGH);
  delay(1000); 

  digitalWrite(redPins[next], LOW);
  digitalWrite(greenPins[next], HIGH);

  activeLane = next;
  Serial.print("Lane ");
  Serial.print(next + 1);
  Serial.println(" is now ACTIVE.");
}
