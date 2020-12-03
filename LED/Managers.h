#include "Segment.h"

#include <ESP8266WiFi.h>
#include <ArduinoJson.h>

#include <SPI.h>
#include <SD.h>

#include <NTPClient.h>
#include <WiFiUdp.h>

#include <string>
#include <vector>

#include <LiquidCrystal_I2C.h>
#include <Wire.h>

class MainManager
{
    //Server connect to WiFi Network
    String ssid = "";
    String password = "";

    //kontener dla wszystkich segmentów
    std::vector <Segment> allData;

    //zmienna na dane otrzymane z aplikacji
    String req = "";

    File myFile ;



    struct timer
    {
      unsigned long actionTime;
      String action;
    };

    std::vector <timer> plannedAction;

    //prywatny konstruktor
    MainManager() {};

  public:
    static MainManager& getInstance() //zwraca jedyną instancję (singleton)
    {
      static MainManager instance; // Guaranteed to be destroyed.
      return instance;
    }
    //Funkcja przyjmująca dane od połączonego klienta i przekazująca ją do funkcji odczytującej dane
    void loadData();

    boolean checkForTask(); //funkcja sprawdzajaca czy nawiazane zostalo polaczenie

    bool readData(bool newData = true);

    void readFile(String filename) ;//funkcja odczytujaca dane z pliku i przetwarzająca je jeśli istniej

    void saveToFile(String filename, String dat = "");

    String printDirectory(File dir);

    void runLeds(); //funkcja wywolujaca glowna funkcje ledow dla kazdego segmentu

    void connectToWifi() ;//funkcja odpowiedzialna za polaczenie z wifi

    void disconnectClient();

    void mloop(); //główna pętla managera- sprawdza czy sa nowe polecenia

    void configure(); //konfiguruje ledy i system plikow

    void configureLCD();

    void LCD(String massageR1, String massageR2 = "");
};
