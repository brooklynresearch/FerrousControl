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

Both current design codes, just spit out what they received on the serial line to the LCD.  LCD output may need to change to some status message, or timing measure, or some other feedback that might be more useful.

### TO DO
- Test timing with a full 1600 values of information
- Test with increase packet size (Arduino has a default of 64 bytes, Teensy 512 bytes)
- Troubleshoot/Fix the RS485 communications between the Teensy and Arduino

### Resources
- [USB Serial Communication](https://www.pjrc.com/teensy/td_serial.html)
- [Serial Benchmark](https://www.pjrc.com/teensy/benchmark_usb_serial_receive.html) 




