#include <Adafruit_NeoPixel.h>

#define PIN        5
#define NUMPIXELS_MAX 80

extern Adafruit_NeoPixel pixels;

void configPixels();

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

    Segment(int n, int d = 0,  int b = 0);

    void clearPixels(); //czyści dane pixeli
    void addPixel(int red, int green, int blue, int i); //funkcja dodająca wartości koloru i indeks
    void ledMain();  //funkcja obsługująca
    
};
