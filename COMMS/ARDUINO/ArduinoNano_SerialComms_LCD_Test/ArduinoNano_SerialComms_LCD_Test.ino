/*
  LiquidCrystal Library - Hello World

 Demonstrates the use a 16x2 LCD display.  The LiquidCrystal
 library works with all LCD displays that are compatible with the
 Hitachi HD44780 driver. There are many of them out there, and you
 can usually tell them by the 16-pin interface.

 This sketch prints "Hello World!" to the LCD
 and shows the time.

  The circuit:
 * LCD RS pin to digital pin 12
 * LCD Enable pin to digital pin 11
 * LCD D4 pin to digital pin 5
 * LCD D5 pin to digital pin 4
 * LCD D6 pin to digital pin 3
 * LCD D7 pin to digital pin 2
 * LCD R/W pin to ground
 * LCD VSS pin to ground
 * LCD VCC pin to 5V
 * 10K resistor:
 * ends to +5V and ground
 * wiper to LCD VO pin (pin 3)

 Library originally added 18 Apr 2008
 by David A. Mellis
 library modified 5 Jul 2009
 by Limor Fried (http://www.ladyada.net)
 example added 9 Jul 2009
 by Tom Igoe
 modified 22 Nov 2010
 by Tom Igoe
 modified 7 Nov 2016
 by Arturo Guadalupi

 This example code is in the public domain.

 http://www.arduino.cc/en/Tutorial/LiquidCrystalHelloWorld

*/

// include the library code:
#include <LiquidCrystal.h>

#define VERSION 0.0
#define DATA_DIR_PIN  2

#define RS485_TRANSMIT  HIGH
#define RS485_RECEIVE   LOW

// initialize the library by associating any needed LCD interface pin
// with the arduino pin number it is connected to
const int rs = 9, en = 8, d4 = 7, d5 = 6, d6 = 5, d7 = 4;

LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

const uint16_t packetSize = 320;
const uint16_t targetByte = 160;
uint16_t byteCount = 0;
uint16_t packetCount = 0;
uint16_t checksum = 0;
uint8_t indicator = 0;


void setup() {
  Serial.begin(1000000);
  pinMode(DATA_DIR_PIN, OUTPUT);
  digitalWrite(DATA_DIR_PIN, RS485_RECEIVE);
  
  // set up the LCD's number of columns and rows:
  lcd.begin(16, 2);
  // Print a message to the LCD.
  lcd.print("NANO: SER TEST");
  lcd.setCursor(0,1);
  lcd.print("VER: ");
  lcd.print(VERSION);
  delay(2000);
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("PKT:");
}

void loop() {
  //lcd.setCursor(4,0);
  uint8_t charIndex = 4;
  uint8_t rowIndex = 0;
  if (Serial.available()) {
    //delay(10);
    while(Serial.available() > 0) {
      uint8_t inByte = Serial.read();
      byteCount++;
      checksum = (checksum + inByte) % 65535; 
      if(byteCount == targetByte) {   
        indicator = inByte;
      }
      if(byteCount == packetSize) {
        lcd.setCursor(charIndex, rowIndex);
        lcd.print(packetCount++);
        lcd.print(" ^:");
        lcd.print(indicator);
        lcd.setCursor(0, 1);
        lcd.print("CHK:");
        lcd.print(checksum);
        Serial.flush();
        byteCount = 0;
        checksum = 0;
      }
    }
  }
}
