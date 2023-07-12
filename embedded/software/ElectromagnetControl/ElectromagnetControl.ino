// include the library code:
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Tlc59711.h>


#define VERSION 1.0
#define DATA_DIR_PIN  2
#define NUM_TLC 2

LiquidCrystal_I2C lcd(0x27, 16, 2);

uint8_t COL = 1;

//#define TESTER
//#define BOARD_TEST
//#define COMMS_TEST

#define ADDR_PIN_1   A0
#define ADDR_PIN_2   A1
#define ADDR_PIN_4   A2
#define ADDR_PIN_8   A3
#define ADDR_PIN_16  10
uint8_t ADDRESS_PIN[5] = {ADDR_PIN_1, ADDR_PIN_2, ADDR_PIN_4, ADDR_PIN_8, ADDR_PIN_16};

uint16_t START_POS = 0;
uint16_t STOP_POS = 24;

#define RS485_TRANSMIT  HIGH
#define RS485_RECEIVE   LOW


#define data    11
#define clock   13
#define led     9

Tlc59711 tlc(NUM_TLC);

#define TOTAL_MAGNETS  24
#define TOTAL_BOARDS  5
#define BAUD  1000000
//#define BAUD  115200
uint8_t magnetOutput[TOTAL_MAGNETS] = {};

#define MULTIPLIER    1

const uint16_t packetSize = TOTAL_MAGNETS * TOTAL_BOARDS;
uint16_t byteCount = 0;
uint8_t magCount = 0;
uint16_t packetCount = 0;
uint16_t checksum = 0;
uint8_t indicator = 0;


void setup() {
  //Serial.begin(115200);
  Serial.begin(BAUD);
  pinMode(DATA_DIR_PIN, OUTPUT);
  digitalWrite(DATA_DIR_PIN, RS485_RECEIVE);

  lcd.init();
  lcd.backlight();

  COL = getBoardAddress();

  lcd.print("NEW HUMANS V02");
  lcd.setCursor(0, 1);
  lcd.print("COL: ");
  lcd.print(COL);
  lcd.print("  BAUD:1M");

#ifdef COMMS_TEST
  Serial.println("-------------------------------------------");
  Serial.println("Electromagnetic Control");
  Serial.print("COL: "); Serial.println(COL);
  Serial.println("-------------------------------------------");
#endif

  switch (COL) {
    case 1:
      START_POS = 0;
      STOP_POS = 24;
      break;
    case 2:
      START_POS = 24;
      STOP_POS = 48;
      break;
    case 3:
      START_POS = 48;
      STOP_POS = 72;
      break;
    case 4:
      START_POS =  72;
      STOP_POS = 96;
      break;
    case 5:
      START_POS = 96;
      STOP_POS = 120;
      break;
    default:
      START_POS = 0;
      STOP_POS = 24;
      break;
  }

  initializeArray();
  tlc.beginFast();
  Wire.setClock(400000);

  killPower();

  delay(1000);
  lcd.clear();
  lcd.print("START:");
  lcd.print(START_POS);
  lcd.setCursor(0, 1);
  lcd.print("STOP:");
  lcd.print(STOP_POS);
  delay(1000);
  lcd.clear();
}

void loop() {
#ifdef BOARD_TEST
  boardTestFullPower();
#else
  readIncomingSerial();
#endif
}

void readIncomingSerial() {

  while (Serial.available() > 0) {
    uint8_t inByte = Serial.read();
    if ((byteCount >= START_POS) && (byteCount < STOP_POS)) {
      magnetOutput[magCount] = constrain(inByte, 0, 255);
      magCount++;
    }
    byteCount++;

    if (byteCount >= packetSize) {
      //lcd.print(COUNTED);
      sendDataToMagnets();
      //lcd.clear();
      magCount = 0;
      byteCount = 0;
    }
  }
}

void debugSerialBuffer() {
  Serial.println("MAG: ");
  Serial.println("----------------");
  for (int y = 0; y < 4; y++) {
    for (int x = 0; x < 16; x++) {
      Serial.print(MULTIPLIER * uint16_t(magnetOutput[y * 16 + x]));
      Serial.print(",");
    }
    Serial.println();
    Serial.println();
  }
}

void initializeArray() {
  for (int i = 0; i < TOTAL_MAGNETS; i++) {
    magnetOutput[i] = 0;
  }
}


void boardTest() {
  for (int i = 0; i < TOTAL_MAGNETS; i++) {
    tlc.setChannel(i, 4096);
  }
  tlc.write();
}

void boardTestFullPower() {
  for (int i = 0; i < TOTAL_MAGNETS; i++) {
    tlc.setChannel(i, 65535);
  }
  tlc.write();
}

void boardTestQuarterPower() {
  for (int i = 0; i < TOTAL_MAGNETS; i++) {
    tlc.setChannel(i, 16384);
  }
  tlc.write();
}

void boardTestThreeEighthsPower() {
  for (int i = 0; i < TOTAL_MAGNETS; i++) {
    tlc.setChannel(i, 8192);
  }
  tlc.write();
}

void boardTestHalfPower() {
  for (int i = 0; i < TOTAL_MAGNETS; i++) {
    tlc.setChannel(i, 32769);
  }
  tlc.write();
}

void killPower() {
  for (int i = 0; i < TOTAL_MAGNETS; i++) {
    tlc.setChannel(i, 0);
  }
  tlc.write();
}


void sendDataToMagnets() {
  for (int i = 0; i < TOTAL_MAGNETS; i++) {
    tlc.setChannel(i, magnetOutput[i]);
  }
  tlc.write();
}


uint8_t getBoardAddress() {
  uint8_t currentAddress = 0;
  for (int i = 0; i < TOTAL_BOARDS; i++) {
    pinMode(ADDRESS_PIN[i], INPUT_PULLUP);
    delay(5);
    bool value = digitalRead(ADDRESS_PIN[i]);
    uint8_t addedValue = (1 << i);
    currentAddress += (!value * addedValue);
  }
  return currentAddress;
}
