#include <ESP8266WiFi.h>
#include <ArduinoJson.h>
#include <string>

#include <Adafruit_NeoPixel.h>
#ifdef _AVR_
#include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif

#define PIN        14 // On Trinket or Gemma, suggest changing this to 1
#define NUMPIXELS_MAX 80

Adafruit_NeoPixel pixels(NUMPIXELS_MAX, PIN, NEO_RGB + NEO_KHZ800);


const short port = 8888;  //Port number
WiFiServer server(port);

//Server connect to WiFi Network
const char *ssid = "UPC3289504";  // wifi SSID
const char *password = "CzsG2tbkj4uc";  // wifi Password

WiFiClient client;
WiFiClient newClient;

//request for led's and file stored in flash memo with last use req
String req = "";
const char* filename = "/samplefile.txt";

void setup()
{
  Serial.begin(115200);

  //zapala wbudowana diode na czas laczenia z siecia
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  Serial.println();

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password); //Connect to wifi

  client.flush();
  client.stop();
  newClient.flush();
  newClient.stop();

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


  Serial.print("Konfiguruję ledy:");
  pixels.begin(); // INITIALIZE NeoPixel strip object
  Serial.println("..... OK");

  Serial.print("Konfiguruję file sys:");
  if (SPIFFS.begin())
    Serial.println("..... OK");
  else
    Serial.println("..... FAILED!");

  //Read File data - check if in file is last used configuration
  File f = SPIFFS.open(filename, "r");

  if (!f) {
    Serial.println("File open failed");
  }
  else
  {
    Serial.print("Reading Data from File:");
    //Data from file
    req = "";
    for (int i = 0; i < f.size(); i++) //Read upto complete file size
      req += (char)f.read();

    f.close();  //Close file
    Serial.println("..... OK");
    Serial.println(req);
    readData();
  }

  Serial.println("Kończę setup");

}
//liczba, jasność, opóźnienie i kolory
unsigned short int num = -1, br = -1, del = 0, r[NUMPIXELS_MAX], g[NUMPIXELS_MAX], b[NUMPIXELS_MAX];
short loop_index = 0; //indeks aktualnie ustawiuanego pixela


void loop()
{
  //jeśli klient nie jest połączony - sprawdza czy jest task
  if (!newClient.connected())
    checkForTask();
  else
  {
    //ustawia klienta i odbiera dane
    client = newClient;
    loadData();
  }

  //funkcja obsługująca ledy
  led();
  pixels.show();
}

//Funkcja przyjmująca dane od połączonego klienta i przekazująca ją do funkcji odczytującej dane
void loadData()
{
  Serial.println("LOAD_DATA - start");
 
  if (client.connected())
  {
    Serial.println("Client Connected");
    
    while (client.connected())
    {
      // Wait until the client sends some data
      Serial.println("new client");

      while (!client.available()) {
        delay(0.5);
      }

      req = client.readStringUntil('\r');
//      Serial.println(req);
      Serial.println("loadData() --passing to--> readData()");
      readData();
      loop_index = 0;
      pixels.clear();


    }

    client.flush();
    client.stop();
    newClient.flush();
    newClient.stop();
    Serial.println("Client disconnected");
  }


  Serial.println("LOAD_DATA - stop");
}

boolean checkForTask() {
  newClient = server.available();
  if (newClient) {
    Serial.println("new client detected.");
    return true;
  }
  return false;
}
void led()
{
  
  pixels.setPixelColor(loop_index, b[loop_index], r[loop_index], g[loop_index]);

  if (br) //ustawia jasnosc
    pixels.setBrightness(br);

  if (del > 0)
  {
    delay(del);
    pixels.show();
  }

  loop_index++;


  if (loop_index > NUMPIXELS_MAX )
  {
    loop_index = 0;

  }

  if (del > 0 && loop_index == 0)
    pixels.clear();


}
bool readData()
{

  //JSON----------------------------------------
  static const size_t capacity = JSON_OBJECT_SIZE(3) + JSON_ARRAY_SIZE(2) + 60;
  DynamicJsonBuffer jsonBuffer(capacity);
  
  // Parse JSON object
  JsonObject& jObj = jsonBuffer.parseObject(req);

  //jesli nie udalo sie odczytac danych - komunikat i zamkniecie polaczenia
  if (!jObj.success())
  {
    Serial.println("No data or parseObject() failed");
    client.flush();
    client.stop();
    newClient.flush();
    newClient.stop();
  }
  else
  {
    //zapisuje poprawne dane do pliku
    File f = SPIFFS.open(filename, "w");

    if (!f) {
      Serial.println("File open failed");
    }
    else
    {
      //Write data to file
      Serial.println("Writing Data to File");
      f.print(req);
      f.close();  //Close file
    }

    
    //odczytuje dane z jsona
    num = jObj["num"];
    br = jObj["brightness"];
    del = jObj["del"];
//    br = (br < 0) ? -1 : br;
    Serial.print(num);
    Serial.print(" ---- ");
    Serial.print(br);
    Serial.print(" ---- ");
    Serial.print(del);
    Serial.print(" ---- ");
    Serial.println();

    //odczytuje dane pixeli
    for (int i = 0; i < num; i++)
    {
      r[i] = int(jObj["L" + String(i)]["red"]);
      g[i] = int(jObj["L" + String(i)]["green"]);
      b[i] = int(jObj["L" + String(i)]["blue"]);
      Serial.print(r[i]);
      Serial.print(" , ");
      Serial.print(g[i]);
      Serial.print(" , ");
      Serial.print(b[i]);
      Serial.println();
    }
  }
}
