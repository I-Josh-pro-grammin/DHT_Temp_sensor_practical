#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>

#define DHTPIN 7
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// I2C LCD address: typically 0x27 or 0x3F for 16x2 displays
LiquidCrystal_I2C lcd(0x27, 16, 2);

// EDIT THIS: Enter candidate name (if > 16 chars, it will scroll automatically)
String candidateName = "IZERE JOSHUA - SPE CANDIDATE"; 

String scrollText = "";
int scrollPos = 0;

unsigned long lastScrollTime = 0;
const unsigned long scrollInterval = 350; // Scroll speed in ms

unsigned long lastSensorTime = 0;
const unsigned long sensorInterval = 2000; // Sensor read interval in ms

float currentTemp = 0.0;

void setup()
{
    Serial.begin(9600);
    
    // Initialize the I2C LCD
    lcd.init();
    lcd.backlight();
    
    dht.begin();

    // Prepare scroll text: add space padding at the end for wrapping
    if (candidateName.length() > 16) {
        scrollText = candidateName + "    ";
    }

    // Initial display
    updateDisplay();
}

void loop()
{
    unsigned long currentMillis = millis();

    // 1. Smooth horizontal scroll for Candidate Name (Row 1)
    if (candidateName.length() > 16) {
        if (currentMillis - lastScrollTime >= scrollInterval) {
            lastScrollTime = currentMillis;
            
            lcd.setCursor(0, 0);
            lcd.print(scrollText.substring(scrollPos, scrollPos + 16));
            
            scrollPos++;
            if (scrollPos > scrollText.length() - 16) {
                scrollPos = 0; // Wrap scroll
            }
        }
    } else {
        // If 16 chars or less, show static name left-aligned
        lcd.setCursor(0, 0);
        lcd.print(candidateName);
        // Pad the rest of the line with spaces
        for (int i = candidateName.length(); i < 16; i++) {
            lcd.print(" ");
        }
    }

    // 2. Read temperature and send to Serial every 2 seconds
    if (currentMillis - lastSensorTime >= sensorInterval) {
        lastSensorTime = currentMillis;
        
        float temp = dht.readTemperature();
        
        // Handle read error gracefully
        if (!isnan(temp)) {
            currentTemp = temp;
            
            // Send to PC Serial
            Serial.println(currentTemp);
            
            // Update the temperature row immediately
            lcd.setCursor(0, 1);
            lcd.print("Temp: ");
            lcd.print(currentTemp);
            lcd.print(" C   ");
        } else {
            // Sensor error
            lcd.setCursor(0, 1);
            lcd.print("Sensor Error    ");
        }
    }
}

// Initial display draw helper
void updateDisplay() {
    lcd.setCursor(0, 0);
    if (candidateName.length() > 16) {
        lcd.print(candidateName.substring(0, 16));
    } else {
        lcd.print(candidateName);
    }
    
    lcd.setCursor(0, 1);
    lcd.print("Initializing...");
}