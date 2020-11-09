#include <ESP8266WiFi.h>
#include <ArduinoJson.h>

#include <Adafruit_NeoPixel.h>

#include <string>
#include <vector>

#define PIN        14 
#define NUMPIXELS_MAX 80

Adafruit_NeoPixel pixels(NUMPIXELS_MAX, PIN, NEO_RGB + NEO_KHZ800);

class Segment
{   
    //zmienne liczby ledów, jasności i opóźnienia
    unsigned short num, br , del;
    
    //indeks aktualnie ustawiuanego pixela
    short loop_index = 0; 
    
    //kolory rgb oraz indeksy kazdedo pixela w segmencie
    std::vector<short> r, g, b, index;

    //zmienne czasu do obsługi opóźnienia
    unsigned long currentMillis, startMillis;

  public:
  
    Segment(int n, int d = 0,  int b = 0)
    {
      num = n;
      br = b;
      del = d;
      
      startMillis = millis();
    }

    void clearPixels() //czyści dane pixeli
    { 
      
      r.clear();
      g.clear();
      b.clear();
      index.clear();
    }

    void addPixel(int red, int green, int blue, int i) //funkcja dodająca wartości koloru i indeks
    { 
      
      r.push_back(red);
      g.push_back(green);
      b.push_back(blue);
      index.push_back(i);
    }

    void ledMain()  //funkcja obsługująca 
    { 

      if (br) //ustawia jasnosc
        pixels.setBrightness(br);

      //sprawdza czy upłynął wymagamy czas nie blokując programu (millis zamiast delay)
      currentMillis = millis();
      if (currentMillis - startMillis >= del)
      {
        //"reset" czasu
        startMillis = currentMillis;
        
        pixels.setPixelColor(index[loop_index], b[loop_index], r[loop_index], g[loop_index]);

        if (del > 0)
          pixels.show();

        loop_index++;

        if (loop_index  >= num )
        {
          loop_index = 0;

          if (del == 0)
            pixels.show();
        }

        if (loop_index == 0 && del != 0)
          pixels.clear();
      }
    }
};




const short port = 8888;  //Port number
WiFiServer server(port);
WiFiClient client;
WiFiClient newClient;

class MainManager
{
    //Server connect to WiFi Network
    const char *ssid = "UPC3289504";  // wifi SSID
    const char *password = "CzsG2tbkj4uc";  // wifi Password

    //kontener dla wszystkich segmentów
    std::vector <Segment> allData;

    //zmienna na dane otrzymane z aplikacji 
    String req = "";
    //plik tekstowy z ostatnimi ustawieniami
    const char* filename = "/samplefile.txt";

    //prywatny konstruktor
    MainManager() {};
  public:
    static MainManager& getInstance() //zwraca jedyną instancję (singleton)
    { 
      static MainManager instance; // Guaranteed to be destroyed.
      return instance;
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

          req = client.readStringUntil('\n');
          Serial.println(req);
          Serial.println("loadData() --passing to--> readData()");

          //jesli dane zaladowane chcemy je odczytac
          readData();
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

    boolean checkForTask() //funkcja sprawdzajaca czy nawiazane zostalo polaczenie 
    {
      newClient = server.available();
      if (newClient) {
        Serial.println("new client detected.");
        return true;
      }
      return false;
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
        //zapisuje polecenie do pliku
        saveToFile();

        //czysci dane wszystkich segmentow
        for ( size_t i = 0; i < allData.size(); i++ )
          allData[i].clearPixels();
        //czysci segmenty
        allData.clear();

        //zmienna przechowujaca liczbe zdefiniowanych ledow
        int definedLEDs = 0;
        
        //odczytuje dane z jsona
        for (int i = 0; i < jObj["SegNum"]; i++)
        {
          //tworzy segment i ,,wklada" go do kontenera
          Segment tmp(jObj["S" + String(i)]["n"], jObj["S" + String(i)]["d"], jObj["S" + String(i)]["br"]);
          allData.push_back(tmp);
          
          definedLEDs += int(jObj["S" + String(i)]["n"]);
          
          //odczytuje dane pixeli
          for (int j = 0; j < jObj["S" + String(i)]["n"]; j++)
          {
            //sprawdza czy indeksy sa zdefiniowane - jesli nie ustawia je automatycznie (po kolei)
            if (jObj["indexing"] == "normal")
              allData[i].addPixel(int(jObj["S" + String(i)]["L" + String(j)]["r"]), int(jObj["S" + String(i)]["L" + String(j)]["g"]), int(jObj["S" + String(i)]["L" + String(j)]["b"]), j);
            else if (jObj["indexing"] == "specified")
              allData[i].addPixel(int(jObj["S" + String(i)]["L" + String(j)]["r"]), int(jObj["S" + String(i)]["L" + String(j)]["g"]), int(jObj["S" + String(i)]["L" + String(j)]["b"]), int(jObj["S" + String(i)]["L" + String(j)]["i"]));
          }

        }

        //jesli nie zdefiniowano wszystkich dostępnych pixeli - ustawia resztę na wyłączone
        if (definedLEDs < NUMPIXELS_MAX)
          for (int x = definedLEDs; x < NUMPIXELS_MAX; x++)
            pixels.setPixelColor(x, 0, 0, 0);
      }

    }

    void readFile() //funkcja odczytujaca dane z pliku i przetwarzająca je jeśli istnieją
    {
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
    }
    
    void saveToFile()
    { //zapisuje poprawne dane do pliku
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
    }

    void runLeds() //funkcja wywolujaca glowna funkcje ledow dla kazdego segmentu
    {
      for ( size_t i = 0; i < allData.size(); i++ )
        allData[i].ledMain();
    }
    
    void connectToWifi() //funkcja odpowiedzialna za polaczenie z wifi
    {
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
    }

};

MainManager manager = MainManager::getInstance();

void setup()
{
  Serial.begin(115200);

  //zapala wbudowana diode na czas laczenia z siecia
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  Serial.println();

  manager.connectToWifi();

  // polaczone -> dioda gasnie
  digitalWrite(LED_BUILTIN, HIGH);




  Serial.print("Konfiguruję ledy:");
  pixels.begin(); // INITIALIZE NeoPixel strip object
  Serial.println("..... OK");

  Serial.print("Konfiguruję file sys:");
  if (SPIFFS.begin())
    Serial.println("..... OK");
  else
    Serial.println("..... FAILED!");

  manager.readFile();
  Serial.println("Kończę setup");
}



void loop()
{
  //jeśli klient nie jest połączony - sprawdza czy jest task
  if (!newClient.connected())
    manager.checkForTask();
  else
  {
    //ustawia klienta i odbiera dane
    client = newClient;
    manager.loadData();
  }

  //funkcja obsługująca ledy
  manager.runLeds();
}
