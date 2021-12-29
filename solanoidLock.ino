#include <AWS_IOT.h>
#include <WiFi.h>

AWS_IOT SecurePermission;

const char* ssid = "WiFiID";
const char* password = "WiFiPW";
char HOST_ADDRESS[] = "AccessPointIDHere"; 
char CLIENT_ID[] = "sungjae";
char sTOPIC_NAME[] = "$aws/things/AWS_smartlock/shadow/update/delta"; // subscribe topic name
char pTOPIC_NAME[] = "$aws/things/AWS_smartlock/shadow/update"; // publish topic name

int status = WL_IDLE_STATUS;
char payload[512];
char rcvdPayload[512];

int msgReceived = 0;
const int CTRL_PIN = 23;
bool LOCKON = false;


void SubscribeCallback (char *topicName, int payloadLen, char *payLoad)
{
  strncpy(rcvdPayload,payLoad,payloadLen);
  rcvdPayload[payloadLen] = 0;
  msgReceived = 1;
  Serial.println("Permission Allow.");
}


void WiFiSetup() {
  Serial.print("WIFI status = ");
  Serial.println(WiFi.getMode());
  WiFi.disconnect(true);
  delay(1000);
  WiFi.mode(WIFI_STA);
  delay(1000);
  Serial.print("WIFI status = ");
  Serial.println(WiFi.getMode()); //++choi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }
  Serial.println("Connected to wifi");
}

void AWS_Setup(){
  if(SecurePermission.connect(HOST_ADDRESS,CLIENT_ID)==0){
      Serial.println("Connected to AWS");
      delay(1000);
    if(0==SecurePermission.subscribe(sTOPIC_NAME,SubscribeCallback)) {
      Serial.println("Subscribe Successfull");
    }
    else {
        Serial.println("Subscribe Failed, Check the Thing Name and Certificates");
        while(1);
      }
    }
    else {
      Serial.println("AWS connection failed, Check the HOST Address");
      while(1);
    }
}

void setup() {
  Serial.begin(115200);
  pinMode(CTRL_PIN, OUTPUT);
  WiFiSetup();
  AWS_Setup();
  digitalWrite(CTRL_PIN,HIGH);

}

void loop() {
  if(msgReceived != 0){
    LOCKON = false;
    digitalWrite(CTRL_PIN,LOW);
    delay(3000);
    digitalWrite(CTRL_PIN,HIGH);
    msgReceived=0;
    LOCKON = true;
  }else{
    LOCKON = true;
  }
}
