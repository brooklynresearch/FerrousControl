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

#define VERSION 16.00
#define DATA_DIR_PIN  2

#define RS485_TRANSMIT  HIGH
#define RS485_RECEIVE   LOW

// initialize the library by associating any needed LCD interface pin
// with the arduino pin number it is connected to
const int rs = 4, en = 5, d4 = 6, d5 = 7, d6 = 8, d7 = 9;

const uint16_t packetSize = 320;
uint8_t byteBuffer[packetSize];
uint32_t packetCount = 0;
uint32_t byteCount = 0;
uint16_t checksum = 0;

LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

void setup() {
  Serial.begin(1000000);
  //Serial1.begin(115200);
  Serial1.begin(1000000);
  Serial2.begin(1000000);
  Serial3.begin(1000000);

  pinMode(DATA_DIR_PIN, OUTPUT);
  digitalWrite(DATA_DIR_PIN, RS485_TRANSMIT);
  
  // set up the LCD's number of columns and rows:
  lcd.begin(16, 2);
  // Print a message to the LCD.
  lcd.print("TEENSY: SER TEST");
  lcd.setCursor(0,1);
  lcd.print("VER: ");
  lcd.print(VERSION);
  delay(2000);
  lcd.clear();
  lcd.setCursor(0,0);
  //lcd.print("PKT:");
  lcd.print(" LEN:");
  lcd.print(packetSize);
}

void loop() {
  //lcd.setCursor(4,0);
  uint8_t charIndex = 4;
  uint8_t rowIndex = 0;
  if (Serial.available()) {
    // wait a bit for the entire message to arrive
    delay(24);
    while(Serial.available() > 0){
      uint8_t inByte = Serial.read();
      byteBuffer[byteCount++] = inByte;
      checksum = (checksum + inByte) % 65535;
      //Serial1.write(inByte);
      if(byteCount == packetSize) {
        Serial1.write(byteBuffer, 320);
        Serial1.flush(); // block until sent
        
        Serial2.write(byteBuffer, 320);
        Serial2.flush(); // block until sent

        Serial3.write(byteBuffer, 320);
        Serial3.flush(); // block until sent

        lcd.setCursor(charIndex, rowIndex);
        lcd.print(inByte);
        /*
        packetCount++;
        /*
        lcd.setCursor(charIndex, rowIndex);
        lcd.print(packetCount);
        lcd.print(" LEN:");
        lcd.print(byteCount);/*
        lcd.setCursor(0,1);
        lcd.print("CHK:");
        lcd.print(checksum);*/
        byteCount = 0;
        checksum = 0;
        Serial.write('$');
      }
    }
  }
  //Serial.println();
}
