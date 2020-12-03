#include "Managers.h"

const short port = 8888;  //Port number
WiFiServer server(port);
WiFiClient client;
WiFiClient newClient;

//dane serwera udostepnianego jesni nie ma sieci do polaczenia
IPAddress local_IP(192, 168, 4, 22);
IPAddress gateway(192, 168, 4, 9);
IPAddress subnet(255, 255, 255, 0);

// Define NTP Client to get time
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org");


int lcdColumns = 16;
int lcdRows = 2;

// set LCD address, number of columns and rows
// if you don't know your display address, run an I2C scanner sketch
LiquidCrystal_I2C lcd = LiquidCrystal_I2C(0x27, lcdColumns, lcdRows); // Change to (0x27,20,4) for 20x4 LCD.

const int buttonPin1 = 16;     // D0
const int buttonPin2 = 15;     // D8
const int buttonPin3 = 4;
// variables will change:
int buttonState1 = 0;         // variable for reading the pushbutton status
int buttonState2 = 0;
int buttonState3 = 0;

void MainManager::configureLCD()
{
  Wire.begin(2, 0);
  // initialize LCD
  lcd.begin();
  // turn on LCD backlight
  lcd.backlight();
}
void MainManager::LCD(String massageR1, String massageR2)
{
  lcd.clear();
  Serial.println(massageR1);
  Serial.println(massageR2);
  Serial.println();

  // set cursor to first column, first row
  lcd.setCursor(0, 0);
  // print message
  lcd.print(massageR1);
  lcd.setCursor(0, 1);
  // print message
  lcd.print(massageR2);
}
void MainManager::configure()
{

  LCD("Konfiguruje:", "ledy");
  pixels.begin(); // INITIALIZE NeoPixel strip object

  LCD("Konfiguruje:", "ledy..... OK");

  LCD("Konfiguruje:", "karte SD");

  if (!SD.begin(1))
    LCD("Konfiguruje:", "karte SD.. FAILED");
  else
    LCD("Konfiguruje:", "karte SD..... OK");


  LCD("Konfiguruje:", "timer");
  timeClient.begin();
  timeClient.setTimeOffset(3600);
  timeClient.update();
  String buffer;
  myFile = SD.open("plannedActions.txt");
  while (myFile.available()) {
    buffer = myFile.readStringUntil('\n');
    Serial.println(buffer); //Printing for debugging purpose
    //do some action here
  }
  myFile.close();

  LCD("Konfiguruje:", "timer..... OK");
  pinMode(buttonPin1, INPUT);
  pinMode(buttonPin2, INPUT);
  pinMode(buttonPin3, INPUT);
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
      LCD("new client");

      while (!client.available()) {
        delay(0.5);
      }
      req = client.readStringUntil('\n');
      Serial.println(req);
      Serial.println("loadData() --passing to--> readData()");
      //jesli dane zaladowane chcemy je odczytac
      readData();
    }

    disconnectClient();

    Serial.println("Client disconnected");
    LCD("Client disconnected");
  }
  Serial.println("LOAD_DATA - stop");
}

void MainManager::disconnectClient()
{
  client.flush();
  client.stop();
  newClient.flush();
  newClient.stop();
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
    disconnectClient();
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
      String tmp = "/SavedOptions/" + jObj["name"].as<String>() + ".txt";


      bool apply = jObj["apply"];

      jObj.remove("OPTION");
      jObj.remove("name");
      jObj.remove("apply");


      String xDDD = "";
      jObj.printTo(xDDD);
      Serial.println("TU:  ");
      Serial.println(xDDD);

      saveToFile(tmp, xDDD);


      disconnectClient();
      if (!apply)
        return 1;

      newData = true;
    }
    else if (jObj["OPTION"] == "LoadF")
    {


      myFile = SD.open("/" + jObj["dir"].as<String>());

      client.println(printDirectory(myFile));
      disconnectClient();
      return 1;
    }
    else if (jObj["OPTION"] == "LoadI")
    {
      String result = "";
      String dir = "/" + jObj["dir"].as<String>() + "/" + jObj["name"].as<String>();

      myFile = SD.open(dir);
      if (myFile) {
        // read from the file until there's nothing else in it:
        while (myFile.available())
          result = myFile.readStringUntil('\n');

        client.println(result);

      }
      myFile.close();
      disconnectClient();
      Serial.println(result);
      return 1;
    }
    else if (jObj["OPTION"] == "timeAction")
    {
      timer tmp_timer;
      tmp_timer.actionTime = jObj["time"];
      tmp_timer.action = jObj["action"].as<String>();

      plannedAction.push_back(tmp_timer);

      std::sort(plannedAction.begin(), plannedAction.end(),
                [](const timer & a, const timer & b) -> bool
      {
        return a.actionTime < b.actionTime;
      });
      saveToFile("plannedActions.txt");
      for (int i = 0; i < plannedAction.size(); i++)
        Serial.println(plannedAction[i].actionTime);
      disconnectClient();
      return 1;
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
      //jesli nie zdefiniowano wszystkich dostepnych pixeli - ustawia reszte na wyłączone
      if (definedLEDs < NUMPIXELS_MAX)
        for (int x = definedLEDs; x < NUMPIXELS_MAX; x++)
          pixels.setPixelColor(x, 0, 0, 0);

    }

  }
  disconnectClient();
}
void  MainManager::readFile(String filename) //funkcja odczytujaca dane z pliku i przetwarzająca je jeśli istnieją
{
  Serial.println("OTWIERAM I CZYTAM Z PLIKU: ");
  Serial.println(filename);
  //Read File data - check if in file is last used configuration
  myFile = SD.open(filename);
  if (myFile)
  {

    Serial.println(filename);

    // read from the file until there's nothing else in it:
    while (myFile.available()) {
      req = myFile.readStringUntil('\n');
    }
    Serial.println(req);
    Serial.println("____");
    readData();
  }
  else
  {
    // if the file didn't open, print an error:
    Serial.print("error opening ");
    Serial.println(filename);
  }
  // close the file:
  myFile.close();
}

void  MainManager::saveToFile(String filename, String dat)
{
  if (dat == "")
    dat = req;

  //zapisuje poprawne dane do pliku
  myFile = SD.open(filename, FILE_WRITE);

  // if the file opened okay, write to it:
  if (myFile) {
    Serial.print("Writing to ");
    Serial.print(filename);
    myFile.println(dat);
    // close the file:
    myFile.close();
    Serial.println(" done.");
  } else {
    // if the file didn't open, print an error:
    Serial.println("error opening test.txt");
  }
}

String MainManager::printDirectory(File dir)
{
  String result = "";

  while (true)
  {

    File entry =  dir.openNextFile();

    // no more files
    if (! entry)
      break;

    result += String(entry.name()) + ";";
    Serial.println(entry.name());
    String dataInside = "";
    while (entry.available()) {
      dataInside = entry.readStringUntil('\n');
    }
    Serial.println(dataInside);
    entry.close();
  }

  return result;
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
  buttonState1 = digitalRead(buttonPin1);
  buttonState2 = digitalRead(buttonPin2);
  buttonState3 = digitalRead(buttonPin3);
  // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
  if (buttonState1 == HIGH)
  {
    // turn LED on:
    Serial.println("1");
    lcd.setCursor(0, 0);
    // print message
    lcd.print("    1");
  }
  if (buttonState2 == HIGH)
  {
    // turn LED on:
    Serial.println("2");
    lcd.setCursor(0, 0);
    // print message
    lcd.print("    2");
  }
  if (buttonState3 == HIGH)
  {
    // turn LED on:
    Serial.println("3");
    lcd.setCursor(0, 0);
    // print message
    lcd.print("    3");
  }

  if (!newClient.connected())
    checkForTask();
  else
  {
    //ustawia klienta i odbiera dane
    client = newClient;
    loadData();
    pixels.clear();
  }


  if (plannedAction.size())
  {
    timeClient.update();
    unsigned long t = timeClient.getEpochTime();
    if ( t >= plannedAction[0].actionTime)
    {
      Serial.print("epoch: ");
      Serial.println(t);

      Serial.print("h: ");
      Serial.println(timeClient.getHours());
      Serial.print("m: ");
      Serial.println(timeClient.getMinutes());

      Serial.print("saved: ");
      Serial.println(plannedAction[0].actionTime);
      String toDo = plannedAction[0].action;
      Serial.println(toDo);
      plannedAction.erase(plannedAction.begin());

      Serial.println("Saving to file...");

      if (SD.exists("plannedAction.txt"))
      {
        Serial.println("Remove plannedAction.txt");
        SD.remove("plannedAction.txt");
      }
      for (int i = 0; i < plannedAction.size(); i++)
      {
        String act = "{\"OPTION\": \"timeAction\", \"time\": 1606210740, \"action\": \"TEST\"}";
        saveToFile("plannedAction.txt", act);
      }

      if (toDo == "OFF")
        readFile("/SavedOptions/OFF.txt");
      else if (toDo == "ON")
        readFile("lastRequest.txt");
      else
        readFile("/SavedOptions/" + toDo + ".txt");


    }
  }


}
