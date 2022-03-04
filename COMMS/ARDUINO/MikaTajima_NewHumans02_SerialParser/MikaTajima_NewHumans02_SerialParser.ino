#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27,16,2);  // set the LCD address to 0x27 for a 16 chars and 2 line display

void setup() {
  lcd.init();
  lcd.backlight();
  lcd.setCursor(2,0);
  lcd.print("MIKA TAJIMA");
  lcd.setCursor(0,1);
  lcd.print("SERIAL PARSER V2");
}

void loop() {
  // put your main code here, to run repeatedly:

}
