from __future__ import print_function, division, absolute_import

import time
import sys
import glob
import serial
import threading
import random
import ctypes, os

from robust_serial import write_order, Order, write_i8, write_i16, read_i8, read_order
from robust_serial.utils import open_serial_port

#Constants:
VERSION = '0.2.0'

#-------------------------------------------------------------------
#FUNCTIONS:
#-------------------------------------------------------------------
#OS-specific low-level timing functions:
if (os.name=='nt'): #for Windows:
    def micros():
        "return a timestamp in microseconds (us)"
        tics = ctypes.c_int64()
        freq = ctypes.c_int64()

        #get ticks on the internal ~2MHz QPC clock
        ctypes.windll.Kernel32.QueryPerformanceCounter(ctypes.byref(tics))
        #get the actual freq. of the internal ~2MHz QPC clock
        ctypes.windll.Kernel32.QueryPerformanceFrequency(ctypes.byref(freq))

        t_us = tics.value*1e6/freq.value
        return t_us

    def millis():
        "return a timestamp in milliseconds (ms)"
        tics = ctypes.c_int64()
        freq = ctypes.c_int64()

        #get ticks on the internal ~2MHz QPC clock
        ctypes.windll.Kernel32.QueryPerformanceCounter(ctypes.byref(tics))
        #get the actual freq. of the internal ~2MHz QPC clock
        ctypes.windll.Kernel32.QueryPerformanceFrequency(ctypes.byref(freq))

        t_ms = tics.value*1e3/freq.value
        return t_ms

elif (os.name=='posix'): #for Linux:

    #Constants:
    CLOCK_MONOTONIC_RAW = 4 # see <linux/time.h> here: https://github.com/torvalds/linux/blob/master/include/uapi/linux/time.h

    #prepare ctype timespec structure of {long, long}
    class timespec(ctypes.Structure):
        _fields_ =\
        [
            ('tv_sec', ctypes.c_long),
            ('tv_nsec', ctypes.c_long)
        ]

    #Configure Python access to the clock_gettime C library, via ctypes:
    #Documentation:
    #-ctypes.CDLL: https://docs.python.org/3.2/library/ctypes.html
    #-librt.so.1 with clock_gettime: https://docs.oracle.com/cd/E36784_01/html/E36873/librt-3lib.html #-
    #-Linux clock_gettime(): http://linux.die.net/man/3/clock_gettime
    # librt = ctypes.CDLL('librt.so.1', use_errno=True)
    # clock_gettime = librt.clock_gettime
    #specify input arguments and types to the C clock_gettime() function
    # (int clock_ID, timespec* t)
    # clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(timespec)]

    def monotonic_time():
        "return a timestamp in seconds (sec)"
        t = timespec()
        #(Note that clock_gettime() returns 0 for success, or -1 for failure, in
        # which case errno is set appropriately)
        #-see here: http://linux.die.net/man/3/clock_gettime
        if clock_gettime(CLOCK_MONOTONIC_RAW , ctypes.pointer(t)) != 0:
            #if clock_gettime() returns an error
            errno_ = ctypes.get_errno()
            raise OSError(errno_, os.strerror(errno_))
        return t.tv_sec + t.tv_nsec*1e-9 #sec

    def micros():
        "return a timestamp in microseconds (us)"
        return monotonic_time()*1e6 #us

    def millis():
        "return a timestamp in milliseconds (ms)"
        return monotonic_time()*1e3 #ms

#Other timing functions:
def delay(delay_ms):
    "delay for delay_ms milliseconds (ms)"
    t_start = millis()
    while (millis() - t_start < delay_ms):
      pass #do nothing
    return

def delayMicroseconds(delay_us):
    "delay for delay_us microseconds (us)"
    t_start = micros()
    while (micros() - t_start < delay_us):
      pass #do nothing
    return


class serialSending(threading.Thread):
    def __init__(self):
        super(serialSending,self).__init__()
    def run(self):
        try:
            serial_file = open_serial_port(baudrate=115200, timeout=None)
        except Exception as e:
            raise e

        is_connected = False
        # Initialize communication with Arduino
        while not is_connected:
            print("Waiting for arduino...")
            write_order(serial_file, Order.HELLO)
            bytes_array = bytearray(serial_file.read(1))
            if not bytes_array:
                time.sleep(2)
                continue
            byte = bytes_array[0]
            if byte in [Order.HELLO.value, Order.ALREADY_CONNECTED.value]:
                is_connected = True

        print("Connected to Arduino")

        motor_speed = -56
        #start_time = millis();
        while True:
            start_time = millis();

            led_state = 0

            if (start_time % 2000) > 1000:
                led_state = 4095

            # Equivalent to write_i8(serial_file, Order.MOTOR.value)
            for i in range(64):

                write_order(serial_file, Order.SERVO)
                write_i16(serial_file, led_state)
                # write_i16(serial_file, random.randint(0, 4095))
                #order = read_order(serial_file)
                delayMicroseconds(300)
                #print("Ordered received: {:?}", order)
                #time.sleep(1)



            #for _ in range(1):
                #order = read_order(serial_file)

                #if(order == Order.RECEIVED):
                #    index += 1
                #    print("RECEIVED: ", index)
                #print("Ordered received: {:?}", order)
            write_order(serial_file, Order.MOTOR)
            write_i8(serial_file, 100)
            #order = read_order(serial_file)

            elapsed_time = millis() - start_time
            print("TOTAL TIME: ", elapsed_time)
            #delay(10)

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
