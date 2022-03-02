// include the library code:
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define VERSION 1.00
#define DATA_DIR_PIN_1  2
#define DATA_DIR_PIN_2  11
#define DATA_DIR_PIN_3  6
#define DATA_DIR_PIN_4  30
#define DATA_DIR_PIN_5  35

#define RS485_TRANSMIT  HIGH
#define RS485_RECEIVE   LOW

#define SERIAL_BAUD     1000000
#define SERIAL_BUF_SIZE 120

const uint16_t packetSize = 600;
uint8_t byteBuffer[packetSize];
uint8_t buffer_1[SERIAL_BUF_SIZE];
uint8_t buffer_2[SERIAL_BUF_SIZE];
uint8_t buffer_3[SERIAL_BUF_SIZE];
uint8_t buffer_4[SERIAL_BUF_SIZE];
uint8_t buffer_5[SERIAL_BUF_SIZE];

uint32_t packetCount = 0;
uint32_t byteCount = 0;
uint16_t checksum = 0;

uint8_t checkByte = 0;


LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Serial.begin(1000000);
  Serial1.begin(SERIAL_BAUD);
  Serial2.begin(SERIAL_BAUD);
  Serial3.begin(SERIAL_BAUD);
  Serial4.begin(SERIAL_BAUD);
  Serial5.begin(SERIAL_BAUD);

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
  lcd.init();                      // initialize the lcd 
  lcd.backlight();
  // Print a message to the LCD.
  lcd.print("NEW HUMANS V02");
  lcd.setCursor(0,1);
  lcd.print("V: ");
  lcd.print(VERSION);
  lcd.print("  B: 1M");
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

      if(byteCount < SERIAL_BUF_SIZE) {
        buffer_1[byteCount] = inByte;
      }

      else if (byteCount < (SERIAL_BUF_SIZE * 2)) {
        buffer_2[byteCount % SERIAL_BUF_SIZE] = inByte;
      }

      else if (byteCount < (SERIAL_BUF_SIZE * 3)) {
        buffer_3[byteCount % SERIAL_BUF_SIZE] = inByte;
      }

      else if (byteCount < (SERIAL_BUF_SIZE * 4)) {
        buffer_4[byteCount % SERIAL_BUF_SIZE] = inByte;
      }

      else {
        buffer_5[byteCount % SERIAL_BUF_SIZE] = inByte;
      }

      ++byteCount;
      
      checksum = (checksum + inByte) % 65535;

      //Serial1.write(inByte);
      if(byteCount == packetSize) {
        Serial1.write(buffer_1, SERIAL_BUF_SIZE);
        Serial1.flush(); // block until sent
        
        Serial3.write(buffer_2, SERIAL_BUF_SIZE);
        Serial3.flush(); // block until sent

        Serial2.write(buffer_3, SERIAL_BUF_SIZE);
        Serial2.flush(); // block until sent

        Serial4.write(buffer_4, SERIAL_BUF_SIZE);
        Serial4.flush(); // block until sent

        Serial5.write(buffer_5, SERIAL_BUF_SIZE);
        Serial5.flush(); // block until sent

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

      if(byteCount == (packetSize - 1)){
        checkByte = inByte;
      }
    }
  }
}
