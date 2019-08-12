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

#define VERSION 3.10
#define DATA_DIR_PIN_1  2
#define DATA_DIR_PIN_2  6
#define DATA_DIR_PIN_3  11
#define DATA_DIR_PIN_4  30
#define DATA_DIR_PIN_5  35

#define RS485_TRANSMIT  HIGH
#define RS485_RECEIVE   LOW

// initialize the library by associating any needed LCD interface pin
// with the arduino pin number it is connected to
const int rs = 36, en =37, d4 = 38, d5 = 39, d6 = 14, d7 = 15;

const uint16_t packetSize = 1600;
uint8_t byteBuffer[packetSize];
uint8_t buffer_1[320];
uint8_t buffer_2[320];
uint8_t buffer_3[320];
uint8_t buffer_4[320];
uint8_t buffer_5[320];
//int byteBuffer[packetSize];
//int buffer_1[320];
//int buffer_2[320];
//int buffer_3[320];
//int buffer_4[320];
//int buffer_5[320];
uint32_t packetCount = 0;
uint32_t byteCount = 0;
uint16_t checksum = 0;

uint8_t checkByte = 0;

LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

void setup() {
  Serial.begin(1000000);
  Serial1.begin(115200);
//  Serial1.begin(1000000);
  Serial2.begin(115200);
  Serial3.begin(115200);
  Serial4.begin(115200);
  Serial5.begin(115200);

  pinMode(DATA_DIR_PIN_1, OUTPUT);
  digitalWrite(DATA_DIR_PIN_1, RS485_TRANSMIT);
  pinMode(DATA_DIR_PIN_2, OUTPUT);
  digitalWrite(DATA_DIR_PIN_2, RS485_TRANSMIT);
  pinMode(DATA_DIR_PIN_3, OUTPUT);
  digitalWrite(DATA_DIR_PIN_3, RS485_TRANSMIT);
  pinMode(DATA_DIR_PIN_4, OUTPUT);
  digitalWrite(DATA_DIR_PIN_4, RS485_TRANSMIT);
  pinMode(DATA_DIR_PIN_5, OUTPUT);
  digitalWrite(DATA_DIR_PIN_5, RS485_TRANSMIT);
  
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

//  for(int i = 0; i < 320; ++i){
//    buffer_1[i] = 127;
//    buffer_2[i] = 117;
//    buffer_3[i] = 107;
//    buffer_4[i] = 97;
//    buffer_5[i] = 87;
//  }
}

void loop() {
  //lcd.setCursor(4,0);
  uint8_t charIndex = 4;
  uint8_t rowIndex = 0;
  if (Serial.available()) {
    // wait a bit for the entire message to arrive
//    delay(24);
    while(Serial.available() > 0){
        uint8_t inByte = Serial.read();

        if(inByte > 127){
          inByte = 127;
        }
        else if (inByte < 0){
          inByte = 0;
        }

      if(byteCount < 320) {
        buffer_1[byteCount] = inByte;
      }

      else if (byteCount < 640) {
        buffer_2[byteCount % 320] = inByte;
      }

      else if (byteCount < 960) {
        buffer_3[byteCount % 320] = inByte;
      }

      else if (byteCount < 1080) {
        buffer_4[byteCount % 320] = inByte;
      }

      else {
        buffer_5[byteCount % 320] = inByte;
      }

      ++byteCount;
      
      checksum = (checksum + inByte) % 65535;

      //Serial1.write(inByte);
      if(byteCount == packetSize) {
        Serial1.write(buffer_1, 320);
        Serial1.flush(); // block until sent
        
        Serial2.write(buffer_2, 320);
        Serial2.flush(); // block until sent

        Serial3.write(buffer_3, 320);
        Serial3.flush(); // block until sent

        Serial4.write(buffer_4, 320);
        Serial4.flush(); // block until sent

        Serial5.write(buffer_5, 320);
        Serial5.flush(); // block until sent

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
        lcd.setCursor(charIndex, rowIndex);
        lcd.print(" LEN:");
        lcd.print(byteCount);
        lcd.setCursor(0,1);
        lcd.print("CHK:");
        lcd.print(checkByte);
        lcd.print("  ");
        byteCount = 0;
        checksum = 0;
//        Serial.write('$');

      }


//
//        lcd.setCursor(charIndex, rowIndex);
//        lcd.print(inByte);
        if(byteCount == 1599){
          checkByte = inByte;
        }
        
      }
    }
  }
