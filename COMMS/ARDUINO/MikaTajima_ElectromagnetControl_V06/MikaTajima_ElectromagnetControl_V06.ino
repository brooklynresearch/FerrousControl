  // include the library code:
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#define VERSION 0.0
#define DATA_DIR_PIN  2

// between 0 and 4
#define COL 0

//#define TESTER
// uncomment to individually go down each pwm
//#define BOARD_TEST
// uncomment to create a print statement to serial line
//#define COMMS_TEST

#ifdef COL
#define START_POS   0
#define STOP_POS    64
#elif  COL == 1
#define START_POS   64
#define STOP_POS    128
#elif  COL == 2
#define START_POS   128
#define STOP_POS    192
#elif  COL == 3
#define START_POS   192
#define STOP_POS    256
#elif  COL == 4
#define START_POS   256
#define STOP_POS    320
#endif


#define RS485_TRANSMIT  HIGH
#define RS485_RECEIVE   LOW


Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(&Wire, 0x40);
Adafruit_PWMServoDriver pwm1 = Adafruit_PWMServoDriver(&Wire, 0x41);
Adafruit_PWMServoDriver pwm2 = Adafruit_PWMServoDriver(&Wire, 0x42);
Adafruit_PWMServoDriver pwm3 = Adafruit_PWMServoDriver(&Wire, 0x43);

Adafruit_PWMServoDriver controllers[4] = {pwm, pwm1, pwm2, pwm3};

#define TOTAL_MAGNETS  64
uint8_t magnetOutput[TOTAL_MAGNETS] = {};

#define MULTIPLIER    16

const uint16_t packetSize = 320;
const uint16_t targetByte = 63;
uint16_t byteCount = 0;
uint16_t packetCount = 0;
uint16_t checksum = 0;
uint8_t indicator = 0;


void setup() {
  Serial.begin(115200);
  pinMode(DATA_DIR_PIN, OUTPUT);
  digitalWrite(DATA_DIR_PIN, RS485_RECEIVE);

  for(int i=0; i<4; i++){
    controllers[i].begin();
    controllers[i].setPWMFreq(1600);
  }

  Wire.setClock(400000);
}

void loop() {
#ifdef BOARD_TEST
  boardTest();
#else
  readIncomingSerial();
#endif
}

void readIncomingSerial(){
  if (Serial.available()) {
    //delay(10);
    while (Serial.available() > 0) {
      uint8_t inByte = Serial.read();
      if ((byteCount >= START_POS)&&(byteCount < STOP_POS)){
        magnetOutput[byteCount] = inByte;
      }
      byteCount++;

      if (byteCount == packetSize) {
        sendDataToMagnets();
#ifdef COMMS_TEST
        debugSerialBuffer();
#endif
        Serial.flush();
        byteCount = 0;
      }
    }
  }
}

void debugSerialBuffer(){
  Serial.println("MAG: ");
  Serial.println("----------------");
  for(int y=0; y<4; y++){
    for(int x=0; x<16; x++){
      Serial.print(MULTIPLIER * uint16_t(magnetOutput[y*16 + x]));
      Serial.print(",");
    }
  Serial.println();
  Serial.println();
  }
}


void boardTest(){
  for (uint16_t i=0; i<4096; i += 8) {
    for (uint8_t pwmnum=0; pwmnum < 16; pwmnum++) {
      controllers[0].setPWM(pwmnum, 0, (i + (4096/16)*pwmnum) % 4096 );
      controllers[1].setPWM(pwmnum, 0, (i + (4096/16)*pwmnum) % 4096 );
      controllers[2].setPWM(pwmnum, 0, (i + (4096/16)*pwmnum) % 4096 );
      controllers[3].setPWM(pwmnum, 0, (i + (4096/16)*pwmnum) % 4096 );
    }
  }
}
void sendDataToMagnets(){
  for(int y=0; y<4; y++){
    for(int x=0; x<16; x++){
      controllers[y].setPWM(x, 0, (MULTIPLIER * uint16_t(magnetOutput[y*16 + x])));
    }
  }
}

void sendDataToMagnetsOLD() {
  for (uint8_t row = 0; row < 4; row++) {
#ifdef TESTER
    Serial.print("ROW:"); Serial.print(row); Serial.print(" ||");
#endif
    for (uint8_t pwmIndex = 0; pwmIndex < 2; pwmIndex++) {
      for (uint8_t col = 0; col < 4; col++) {
        uint8_t arrayIndex = (row * 8 + pwmIndex * 4 + col);
        uint8_t magIndex = (row * 4 + col);
#ifdef TESTER
        Serial.print("\t"); Serial.print(arrayIndex); Serial.print("|"); Serial.print(magnetOutput[magIndex]);
#endif
        controllers[pwmIndex].setPWM(magIndex, 0, magnetOutput[arrayIndex]);
      }
    }
#ifdef TESTER
    Serial.println();
#endif
  }
  for (uint8_t row = 0; row < 4; row++) {
#ifdef TESTER
    Serial.print("ROW:"); Serial.print(row + 4); Serial.print("||");
#endif
    for (uint8_t pwmIndex = 2; pwmIndex < 4; pwmIndex++) {
      for (uint8_t col = 0; col < 4; col++) {
        uint8_t arrayIndex = ((row + 4) * 8 + (pwmIndex - 2) * 4 + col);
        uint8_t magIndex = (row * 4 + col);
#ifdef TESTER
        Serial.print("\t"); Serial.print(arrayIndex); Serial.print("|"); Serial.print(magnetOutput[magIndex]);
#endif
        controllers[pwmIndex].setPWM(magIndex, 0, magnetOutput[arrayIndex]);
      }
    }
#ifdef TESTER
    Serial.println();
#endif
  }
}
