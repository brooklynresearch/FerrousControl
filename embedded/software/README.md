# Software
Arduino Based Code for both the Electromagnetic Controller and Serial Parser.

## Notes on the Electromagnetic Control
Code was based on the atmega328 chip set, however due to supply chain issues we used the atmega168 chip set.
Regardless, we needed to modify the hardware serial buffer to support 256 bytes, which was required in order to allow for full throughput of serial data.  The default serial buffer size is set to 64 bytes, and would cause overflow on the data being received on the RS485 line.
Liquid Crystal display is not needed, an only used for testing and feedback purposes.  It can be removed if needed.

## Notes on the Serial Parser
Code was based on the Teensy 4.0 development board.  
Liquid Cyrstal display is not needed, an only used for testing and feedback purposes.  It can be removed if needed.

## Platform
- Tested on Arduino 2.11

## Dependencies
- TLC59711 Library 
- LiquidCrystal_I2C library
- Wire Library 
