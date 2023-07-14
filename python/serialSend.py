import sys
import glob
import time
import serial
import threading
import random

TOTAL_MAGS = 256

class serialSending(threading.Thread):
    def __init__(self):
        super(serialSending,self).__init__()
    def run(self):

        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        index = 0
        #PRINT OUT SERIAL PORTS ON THE CONSOLE
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
                print("PORT " + str(index) + ": " + port)
                index += 1
            except (OSError, serial.SerialException):
                pass
        

        magField = ''

        ser = serial.Serial(result[0], 115200, timeout=0)
        #ser = serial.Serial('COM4', 115200, timeout=0)

        #SERIAL DATA FORMAT
        #<MAG value1, value2, ..., valueX, >
        #ex: <MAG 235, 42, 19, 0, 100, >
        while True:
            magField = "<MAG "
            for row in range(TOTAL_MAGS):
                magField += str(random.randint(1,255))
                magField += ","
            magField += " >"
            ser.write(magField.encode('utf-8'))


if __name__ ==  '__main__':

    try:
        thread=serialSending()
        thread.daemon=True
        thread.start()
        while True: 
            #Code Stuffs
            time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        print('\n! Received keyboard interrupt, quitting threads.\n')