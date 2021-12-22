#include <ESP32_Servo.h>
#include <AWS_IOT.h>
#include <WiFi.h>
#include <Arduino_JSON.h>

AWS_IOT testButton;
const char* ssid = "HelloWirelessDCD3";
const char* password = "1707011241";
char HOST_ADDRESS[] = "a3rrs47k7tk6a-ats.iot.ap-northeast-2.amazonaws.com"; 
char CLIENT_ID[] = "jaewoo";
char sTOPIC_NAME[] = "$aws/things/light_switch/shadow/update/delta"; // subscribe topic name
char pTOPIC_NAME[] = "$aws/things/light_swtich/shadow/update"; // publish topic name

int status = WL_IDLE_STATUS; 
int msgCount=0, msgReceived = 0; 
char payload[512];
char rcvdPayload[512];
//const int buttonPin = 15; // pushbutton pin unsigned long preMil = 0;
const long intMil = 10000;
unsigned long preMil = 0;

static const int buttonPin = 15;
static const int leftServoPin = 13;
static const int rightServoPin = 12;
Servo leftServo, rightServo;

long lastDebounceTime = 0;
long debounceDelay = 50;
int lastButtonState = HIGH;
int buttonState = HIGH;
String lightState="OFF";

void mySubCallBackHandler (char *topicName, int payloadLen, char *payLoad) {
  strncpy(rcvdPayload,payLoad,payloadLen); 
  rcvdPayload[payloadLen] = 0; 
  msgReceived = 1;
}

void setup() {
  Serial.begin(115200);
  pinMode(buttonPin, INPUT);
  leftServo.attach(leftServoPin);
  rightServo.attach(rightServoPin);

  Serial.println(WiFi.getMode());
  WiFi.disconnect(true);
  delay(1000);
  WiFi.mode(WIFI_STA);
  delay(1000);
  Serial.print("WIFI status = ");
  Serial.println(WiFi.getMode());
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi.."); 
  }
  Serial.println("Connected to wifi");

  if(testButton.connect(HOST_ADDRESS,CLIENT_ID)== 0) { 
    Serial.println("Connected to AWS");
    delay(1000); 
    if(0==testButton.subscribe(sTOPIC_NAME,mySubCallBackHandler)) {
      Serial.println("Subscribe Successfull"); 
    }
    else {
      Serial.println("Subscribe Failed, Check the Thing Name and Certificates");
      while(1); 
    }
  } else {
    Serial.println("AWS connection failed, Check the HOST Address");
    while(1); 
  }
  // initialize the pushbutton pin as an input pinMode(buttonPin, INPUT);
  delay(2000);
}

void loop() {
  if(msgReceived == 1) {
    msgReceived = 0; 
    Serial.print("Received Message:"); 
    Serial.println(rcvdPayload);
    // Parse JSON
    JSONVar myObj = JSON.parse(rcvdPayload); 
    JSONVar state = myObj["state"];
    JSONVar desired = state["desired"];
    String led = (const char*) state["light"];
    Serial.println(led);
    if(led=="ON" && lightState=="OFF") {
      lightState="ON";
      onLight();
    }
    else if(led=="OFF" && lightState=="ON") {
      lightState="OFF";
      offLight();
    }
  }
  
  if((millis()-preMil) > intMil) {
    // read the state of the pushbutton value if (digitalRead(buttonPin)) {
    preMil = millis();
    if(lightState=="OFF")
      sprintf(payload,"{\"state\":{\"reported\":{\"light\":\"OFF\"}}}");
    else if(lightState=="ON")
      sprintf(payload,"{\"state\":{\"reported\":{\"light\":\"ON\"}}}");
    if(testButton.publish(pTOPIC_NAME,payload) == 0) {
      Serial.print("Publish Message:");
      Serial.println(payload); 
    }
    else
      Serial.println("Publish failed");
  }
  /*
  int reading = digitalRead(buttonPin);
  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }
  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (reading != buttonState) {
      buttonState = reading;
      if (reading == HIGH) {
        pushButton();
      }
    }
  }
  lastButtonState = reading;
  */
}
/*
void pushButton() {
  Serial.println("light on");
  
  for (int posDegrees = 0; posDegrees <= 45; posDegrees++) {
    leftServo.write(posDegrees);
    delay(20);
  }
  delay(50);
  for (int posDegrees = 45; posDegrees >= 0; posDegrees--) {
    leftServo.write(posDegrees);
    delay(20);
  }

  delay(2000);
  
  Serial.println("light off");
  for (int posDegrees = 130; posDegrees <= 160; posDegrees++) {
    rightServo.write(posDegrees);
    delay(20);
  }
  delay(50);
  for (int posDegrees = 160; posDegrees >= 130; posDegrees--) {
    rightServo.write(posDegrees);
    delay(20);
  }
}
*/

void onLight() {
  Serial.println("light on");
  
  for (int posDegrees = 0; posDegrees <= 45; posDegrees++) {
    leftServo.write(posDegrees);
    delay(20);
  }
  delay(50);
  for (int posDegrees = 45; posDegrees >= 0; posDegrees--) {
    leftServo.write(posDegrees);
    delay(20);
  }
}

void offLight(){
  Serial.println("light off");
  for (int posDegrees = 130; posDegrees <= 160; posDegrees++) {
    rightServo.write(posDegrees);
    delay(20);
  }
  delay(50);
  for (int posDegrees = 160; posDegrees >= 130; posDegrees--) {
    rightServo.write(posDegrees);
    delay(20);
  }
}
