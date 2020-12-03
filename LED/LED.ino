#include "Managers.h"

MainManager manager = MainManager::getInstance();

void setup()
{
  Serial.begin(115200);
  manager.configureLCD();

  manager.configure();
  
  manager.readFile("/WiFi_Data.txt");
  manager.readFile("lastRequest.txt");
  manager.readFile("plannedActions.txt");


  manager.connectToWifi();
  Serial.println("Kończę setup");
}

void loop()
{ 
  manager.mloop();

  //funkcja obsługująca ledy
  manager.runLeds();
//  manager.LCD("TEST","ELO");
}
