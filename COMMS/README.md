# FerrousControl
Ferrofluid controlled through an electromagnetic array

## COMMS
Requirements:
- Python 3.6.2
- PySerial
- [Robust Serial Library](https://github.com/araffin/arduino-robust-serial)

## ARDUINO
Requirements:
- [Teensyduino](https://www.pjrc.com/teensy/teensyduino.html)
- [MiniCore] (https://github.com/MCUdude/MiniCore)
- [LiquidCrystal_I2C] (https://github.com/johnrickman/LiquidCrystal_I2C)
- [TLC59711] (https://github.com/s-light/ulrichstern_Tlc59711/tree/master/examples)

Both current design codes, just spit out what they received on the serial line to the LCD.  LCD output may need to change to some status message, or timing measure, or some other feedback that might be more useful.

### TO DO
- Confirm communications between Serial Parser and Electromagnetic Control
- Confirm proper values being received at the view buffer size of 600 Bytes per Teensy, 120 Bytes per Serial Line, and 24 Bytes per Arduino

### Resources
- [USB Serial Communication](https://www.pjrc.com/teensy/td_serial.html)
- [Serial Benchmark](https://www.pjrc.com/teensy/benchmark_usb_serial_receive.html)
- [TLC59711 Datasheet] (https://www.ti.com/lit/ds/symlink/tlc59711.pdf?ts=1646183361798&ref_url=https%253A%252F%252Fwww.google.com%252F) 




