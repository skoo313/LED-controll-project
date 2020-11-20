#include "Managers.h"

const short port = 8888;  //Port number
WiFiServer server(port);
WiFiClient client;
WiFiClient newClient;

//dane serwera udostepnianego jesni nie ma sieci do polaczenia
IPAddress local_IP(192, 168, 4, 22);
IPAddress gateway(192, 168, 4, 9);
IPAddress subnet(255, 255, 255, 0);

void MainManager::configure()
{
  Serial.print("Konfiguruję ledy:");
  pixels.begin(); // INITIALIZE NeoPixel strip object
  Serial.println("..... OK");


  Serial.print("Konfiguruję kartę SD...");

  if (!SD.begin(4))
    Serial.print("initialization failed!");
  else
    Serial.println("..... OK");

}
//Funkcja przyjmująca dane od połączonego klienta i przekazująca ją do funkcji odczytującej dane
void  MainManager::loadData()
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
    }
    client.flush();
    client.stop();
    newClient.flush();
    newClient.stop();
    Serial.println("Client disconnected");
  }
  Serial.println("LOAD_DATA - stop");
}

boolean  MainManager::checkForTask() //funkcja sprawdzajaca czy nawiazane zostalo polaczenie
{
  newClient = server.available();
  if (newClient) {
    Serial.println("new client detected.");
    return true;
  }
  return false;
}
bool  MainManager::readData(bool newData)
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

    if (jObj["OPTION"] == "WifiConfig")
    {
      Serial.println("New Wifi data request");
      ssid = jObj["ssid"].as<String>();
      password = jObj["password"].as<String>();

      if (newData)
        saveToFile("WiFi_Data.txt");

      Serial.println("readDataFun()");
      Serial.println(ssid);
      Serial.println(password);

      return 1;

    }
    else if (jObj["OPTION"] == "Save")
    {
      Serial.println("New data to save");
      String tmp = jObj["name"].as<String>() + ".txt";
      saveToFile(tmp);

      if (!jObj["apply"])
        return 1;
      newData = true;
    }

    //zapisuje polecenie do pliku
    if (newData)
    {
      Serial.println("Saving to file...");


      if (SD.exists("lastRequest.txt"))
      {
        Serial.println("Remove lastRequest.txt");
        SD.remove("lastRequest.txt");
      }
      saveToFile("lastRequest.txt");


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
}
void  MainManager::readFile(String filename) //funkcja odczytujaca dane z pliku i przetwarzająca je jeśli istnieją
{
  Serial.println("OTWIERAM I CZYTAM Z PLIKU: ");
  Serial.println(filename);
  //Read File data - check if in file is last used configuration
  myFile = SD.open(filename);
  if (myFile) {

    Serial.println(filename);

    // read from the file until there's nothing else in it:
    while (myFile.available()) {
      req = myFile.readStringUntil('\n');
    }
    Serial.println(req);
    Serial.println("____");
    readData(false);
  } else {
    // if the file didn't open, print an error:
    Serial.print("error opening ");
    Serial.println(filename);
  }
  // close the file:
  myFile.close();
}
void  MainManager::saveToFile(String filename)
{
  //zapisuje poprawne dane do pliku
  myFile = SD.open(filename, FILE_WRITE);

  // if the file opened okay, write to it:
  if (myFile) {
    Serial.print("Writing to ");
    Serial.print(filename);
    myFile.println(req);
    // close the file:
    myFile.close();
    Serial.println("done.");
  } else {
    // if the file didn't open, print an error:
    Serial.println("error opening test.txt");
  }
}
void  MainManager::runLeds() //funkcja wywolujaca glowna funkcje ledow dla kazdego segmentu
{
  for ( size_t i = 0; i < allData.size(); i++ )
    allData[i].ledMain();
}
void  MainManager::connectToWifi() //funkcja odpowiedzialna za polaczenie z wifi
{
  server.stop();
  server.close();
  Serial.println("_________connectToWifi()");
  Serial.println(ssid);
  Serial.println(password);
  //jesli nie ma sieci do ktorej ma sie polaczyc tworzy swoja
  if (ssid == "")
  {
    Serial.print("Setting soft-AP configuration ... ");
    Serial.println(WiFi.softAPConfig(local_IP, gateway, subnet) ? "Ready" : "Failed!");
    Serial.print("Setting soft-AP ... ");
    Serial.println(WiFi.softAP("ESPsoftAP_01") ? "Ready" : "Failed!");
    Serial.print("Soft-AP IP address = ");
    Serial.println(WiFi.softAPIP());
    server.begin();
  }
  else
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
}
void MainManager::mloop()//jeśli klient nie jest połączony - sprawdza czy jest task
{
  if (!newClient.connected())
    checkForTask();
  else
  {
    //ustawia klienta i odbiera dane
    client = newClient;
    loadData();
    pixels.clear();
  }
}
