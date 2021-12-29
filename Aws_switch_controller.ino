// IoT07-1 ESP32 WebServer에서  수정
#define SWAP 0 // sw access point
// Load Wi-Fi library
#include <WiFi.h>
#include <AWS_IOT.h>

// Replace with your network credentials
#if SWAP
  const char* ssid = "";
  const char* password = ""; // password should be long!!
#else
  const char* ssid = "";
  const char* password = "";    //your wifi password here
#endif

// Set web server port number to 80
WiFiServer server(80);

// AWS IoT
AWS_IOT testButton;
char HOST_ADDRESS[] = "AccesssPointAddressHere"; 
char CLIENT_ID[] = "con-server";
char pTOPIC_NAME[] = "$aws/things/light_switch/shadow/update"; // publish
char payload[512];

// Variable to store the HTTP request
String header;
// Auxiliar variables to store the current output state
String output16State = "off";
String output17State = "off";
// Assign output variables to GPIO pins
const int output16 = 16;
const int output17 = 17;
// Current time
unsigned long currentTime = millis();
// Previous time
unsigned long previousTime = 0;
// Define timeout time in milliseconds (example: 2000ms = 2s)
const long timeoutTime = 2000;

void setup() {
  Serial.begin(115200);
  // Initialize the output variables as outputs
  pinMode(output16, OUTPUT);
  pinMode(output17, OUTPUT);
  // Set outputs to LOW
  digitalWrite(output16, LOW);
  digitalWrite(output17, LOW);
  #if SWAP
    WiFi.softAP(ssid, password);
    IPAddress IP = WiFi.softAPIP();
    Serial.print("AP IP address: ");
    Serial.println(IP);
  #else
  // Connect to Wi-Fi network with SSID and password
    Serial.print("Connecting to ");
    Serial.println(ssid);
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    // Print local IP address and start web server
    Serial.println("");
    Serial.println("WiFi connected.");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
  #endif
  
  server.begin();
  if(testButton.connect(HOST_ADDRESS,CLIENT_ID)== 0) { 
    Serial.println("Connected to AWS");
  } else {
    Serial.println("AWS connection failed, Check the HOST Address");
    while(1); 
  }
  // initialize the pushbutton pin as an input pinMode(buttonPin, INPUT);
  delay(2000);
}

void loop(){
  WiFiClient client = server.available(); // Listen for incoming clients
  if (client) { // If a new client connects,
    currentTime = millis();
    previousTime = currentTime;
    Serial.println("New Client."); // print a message out in the serial port
    String currentLine = ""; // make a String to hold incoming data from the client
    while (client.connected() && currentTime - previousTime <= timeoutTime) { // loop while the client's connected
      currentTime = millis();
      if (client.available()) { // if there's bytes to read from the client,
        char c = client.read(); // read a byte, then
        Serial.write(c); // print it out the serial monitor
        header += c;
        if (c == '\n') { // if the byte is a newline character
          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0) {
            // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
            // and a content-type so the client knows what's coming, then a blank line:
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println("Connection: close");
            client.println();
            // turns the GPIOs on and off
            if (header.indexOf("GET /16/on") >= 0) {
              sprintf(payload,"{\"state\":{\"desired\":{\"light\":\"ON\"}}}");
              if(testButton.publish(pTOPIC_NAME,payload) == 0) {
                Serial.print("Publish Message:");
                Serial.println(payload);
                Serial.println("Light 16 on");
                output16State = "on";
              } else {
                Serial.println("Publish failed");
              }
              //digitalWrite(output16, HIGH);
            } else if (header.indexOf("GET /16/off") >= 0) {
              sprintf(payload,"{\"state\":{\"desired\":{\"light\":\"OFF\"}}}");
              if(testButton.publish(pTOPIC_NAME,payload) == 0) {
                Serial.print("Publish Message:");
                Serial.println(payload);
                Serial.println("Light 16 off");
                output16State = "off";
              } else {
                Serial.println("Publish failed");
              }
              //digitalWrite(output16, LOW);
            }
            
            // Display the HTML web page
            client.println("<!DOCTYPE html><html>");
            client.println("<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">");
            client.println("<link rel=\"icon\" href=\"data:,\">");
            // CSS to style the on/off buttons
            // Feel free to change the background-color and font-size attributes to fit your preferences
            client.println("<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}");
            client.println(".button { background-color: #4CAF50;border: none; color: white; padding: 16px 40px;");
            client.println("text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}");
            client.println(".button2 {background-color: #555555;}</style></head>");
            // Web Page Heading
            client.println("<body><h1>ESP32 Light Controller</h1>");
            // Display current state, and ON/OFF buttons for GPIO 16
            client.println("<p>Light - State " + output16State + "</p>");
            // If the output16State is off, it displays the ON button
            if (output16State=="off") {
            client.println("<p><a href=\"/16/on\"><button class=\"button\">ON</button></a></p>");
            } else {
            client.println("<p><a href=\"/16/off\"><button class=\"button button2\">OFF</button></a></p>");
            }
            // Display current state, and ON/OFF buttons for GPIO 17
//            client.println("<p>GPIO 17 - State " + output17State + "</p>");
//            // If the output17State is off, it displays the ON button
//            if (output17State=="off") {
//            client.println("<p><a href=\"/17/on\"><button class=\"button\">ON</button></a></p>");
//            } else {
//            client.println("<p><a href=\"/17/off\"><button class=\"button button2\">OFF</button></a></p>");
//            }
            client.println("</body></html>");
            // The HTTP response ends with another blank line
            client.println();
            // Break out of the while loop
            break;
          } //** if (currentLine.length() == 0) {
          else { // if you got a newline, then clear currentLine
            currentLine = "";
          }
        } //** if (c == '\n') {
        else if (c != '\r') { // if you got anything else but a carriage return character,
          currentLine += c; // add it to the end of the currentLine
        }
      } //* if (client.available()) {
    } //** while
    // Clear the header variable
    header = "";
    // Close the connection
    client.stop();
    Serial.println("Client disconnected.");
    Serial.println("");
  } //** if (client) {
} //** loop() {
