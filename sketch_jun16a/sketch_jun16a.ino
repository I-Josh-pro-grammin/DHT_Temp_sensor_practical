#include <LiquidCrystal.h>
#include <DHT.h>

#define DHTPIN 7
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

LiquidCrystal lcd(12,11,5,4,3,2);

String candidateName = "Your Full Candidate Name";

int scrollPos = 0;

void setup()
{
    Serial.begin(9600);

    lcd.begin(16,2);

    dht.begin();
}

void loop()
{
    float temperature = dht.readTemperature();

    String scrollText = candidateName + "    ";

    lcd.setCursor(0,0);

    if(candidateName.length() > 16)
    {
        lcd.print(
          scrollText.substring(
             scrollPos,
             scrollPos + 16
          )
        );

        scrollPos++;

        if(scrollPos >
           scrollText.length()-16)
        {
            scrollPos = 0;
        }
    }
    else
    {
        lcd.print(candidateName);
    }

    lcd.setCursor(0,1);

    lcd.print("Temp:");
    lcd.print(temperature);
    lcd.print("C   ");

    Serial.println(temperature);

    delay(1000);
}