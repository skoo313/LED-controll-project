#include "Managers.h"

MainManager manager = MainManager::getInstance();

void setup()
{
  Serial.begin(115200);

  //zapala wbudowana diode na czas laczenia z siecia
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  Serial.println();

  // polaczone -> dioda gasnie
  digitalWrite(LED_BUILTIN, HIGH);

  Serial.print("Konfiguruję file sys:");
  if (SPIFFS.begin())
    Serial.println("..... OK");
  else
    Serial.println("..... FAILED!");
  manager.configure();
  manager.readFile("/WiFi_Data.txt");
  manager.readFile("lastRequest.txt");
  
  
  manager.connectToWifi();
  Serial.println("Kończę setup");
}

void loop()
{
  manager.mloop();

  //funkcja obsługująca ledy
  manager.runLeds();
}
