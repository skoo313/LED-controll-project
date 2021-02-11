#include "Segment.h"

Adafruit_NeoPixel pixels(NUMPIXELS_MAX, PIN, NEO_RGB + NEO_KHZ800);



Segment::Segment(int n, int d,  int b)
{
  num = n;
  br = b;
  del = d;
  startMillis = millis();
}

void Segment::clearPixels() //czyści dane pixeli
{
  r.clear();
  g.clear();
  b.clear();
  index.clear();
}

void Segment::addPixel(int red, int green, int blue, int i) //funkcja dodająca wartości koloru i indeks
{
  r.push_back(red);
  g.push_back(green);
  b.push_back(blue);
  index.push_back(i);
}

void Segment::ledMain()  //funkcja obsługująca
{
  if (!clearing)
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
        clearing = true;
        if (del == 0)
          pixels.show();
      }
    }
  }
  else
  {
    pixels.setPixelColor(index[loop_index], 0, 0, 0);
    loop_index++;
    if (loop_index  >= num )
    {
      loop_index = 0;
      clearing = false;
    }
  }
}
