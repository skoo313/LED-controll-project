#include <ESP8266WiFi.h>
#include <ArduinoJson.h>
#include <string>

#include <Adafruit_NeoPixel.h>
#ifdef _AVR_
#include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif

#define PIN        14 // On Trinket or Gemma, suggest changing this to 1
#define NUMPIXELS 80 

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_RGB + NEO_KHZ800);
#define DELAYVAL 0 // Time (in milliseconds) to pause between pixels
#define SendKey 0  //Button to send data Flash BTN on NodeMCU

int port = 8888;  //Port number
WiFiServer server(port);

//Server connect to WiFi Network
const char *ssid = "UPC3289504";  // wifi SSID
const char *password = "CzsG2tbkj4uc";  // wifi Password

void setup()
{
  Serial.begin(115200);

  //zapala wbudowana diode na czas laczenia z siecia
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  Serial.println();

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password); //Connect to wifi

  // Wait for connection
  Serial.println("Connecting to Wifi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    delay(500);
  }
  // polaczone -> dioda gasnie
  digitalWrite(LED_BUILTIN, HIGH);

  //drukowanie informacji o polaczeniu
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
  server.begin();
  Serial.print("Connect to:");
  Serial.print(WiFi.localIP());
  Serial.print(":");
  Serial.println(port);


  Serial.println("Konfiguruję ledy");
  pixels.begin(); // INITIALIZE NeoPixel strip object
  Serial.println("Kończę setup");
}

void getData(String req)
{

  //JSON----------------------------------------
  const size_t capacity = JSON_OBJECT_SIZE(3) + JSON_ARRAY_SIZE(2) + 160;

  DynamicJsonBuffer jsonBuffer(capacity);

  // Parse JSON object
  JsonObject& json_object = jsonBuffer.parseObject(req);
  if (!json_object.success()) {
    
    Serial.println("No data or parseObject() failed");
  }
  else
  {
    light_leds(json_object);
  }
}
void light_leds(JsonObject &jObj)
{

  int num = jObj["num"];

  int redTab[num];
  int greenTab[num];
  int blueTab[num];
  int red , green , blue, brightness=-1;

  if (num == 1)
  {
    red = jObj["r"];
    green = jObj["g"];
    blue = jObj["b"];
    brightness = jObj["brightness"];
  }
  else
  {
    for (int i = 0; i < num; i++)
    {
      String numR= "r"+String(i);
      String numG= "g"+String(i);
      String numB= "b"+String(i);

      redTab[i] = jObj[numR];
      greenTab[i] = jObj[numG];
      blueTab[i] = jObj[numB];

    }
    
  }
  
  //czysci zapisane ustawienia
  pixels.clear();
  int looplim;

  if(num==1)
    looplim=NUMPIXELS;
  else
    looplim=num;
  // dla kazdego ,,pixela''
  for (int i = 0; i < looplim; i++)
  {
    if (num == 1) //ustawia barwe
      pixels.setPixelColor(i, blue, red, green);
    else
      pixels.setPixelColor(i, blueTab[i], redTab[i], greenTab[i]);

    if (brightness > 0) //ustawia jasnosc
      pixels.setBrightness(brightness);

    //delay(DELAYVAL); // Pause before next pass through loop
  }
  pixels.show();
}

void loop()
{
  // umorzliwia polaczenie i ustaiwa timeOut'a
  WiFiClient client = server.available();
  client.setTimeout(100);

  // zmienna dla otrzymywanych danych
  static String req;
  Serial.println(req);
  //=========== OBSŁUGA POŁĄCZENIA ===================
  if (client)
  {
    if (client.connected())
    {
      Serial.println("Client Connected");
      client.println("Hello, client!");
    }

    while (client.connected())
    {
      // Wait until the client sends some data
      Serial.println("new client");

      int er_num=0;
      while (!client.available()) {
        delay(0.5);
      }
      req = client.readStringUntil('\r');


      client.flush();
    }
    client.stop();
    Serial.println("Client disconnected");
  }
  //----------------------------------------

  // przekazanie stringa z otrzymanymi danymi do funkcji
  getData(req);
}
