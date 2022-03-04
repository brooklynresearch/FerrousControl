// include the library code:
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Tlc59711.h>

#define VERSION 1.00

#define data    11
#define clock   13
#define led     9
#define NUM_TLC 2

Tlc59711 tlc(NUM_TLC);

#define RS485_TRANSMIT  HIGH
#define RS485_RECEIVE   LOW
#define DATA_DIR_PIN    2

#define SERIAL_BAUD     1000000
#define SERIAL_BUF_SIZE 120

#define TOTAL_MAGNETS   24
#define DELAY           500

const uint16_t packetSize = 600;
uint8_t byteBuffer[packetSize];


uint32_t packetCount = 0;
uint32_t byteCount = 0;
uint16_t checksum = 0;

uint8_t checkByte = 0;


LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Serial.begin(1000000);

  lcd.init();
  lcd.backlight();

  tlc.beginFast();
  
  // set up the LCD's number of columns and rows:
  lcd.begin(16, 2);
  // Print a message to the LCD.
  lcd.print("NEW HUMANS V02");
  lcd.setCursor(0,1);
  lcd.print("MAG TEST  V:");
  lcd.print(VERSION);
  delay(2000);
  lcd.clear();
}

void loop() {
 for (int i = 0; i < TOTAL_MAGNETS; i++) {
    tlc.setChannel(i, 65535);
    tlc.write();
    lcd.setCursor(0,0);
    lcd.print("MAG: ");
    lcd.print(i + 1);
    lcd.print("  ");
    lcd.setCursor(0,1);
    lcd.print("ON ");
    delay(DELAY);
    tlc.setChannel(i,0);
    tlc.write();
    lcd.setCursor(0,1);
    lcd.print("OFF");
    delay(DELAY);
  }
  
 
}
