#!/usr/bin/env python3
import serial
import time
if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    ser.reset_input_buffer()
    while True:
        ser.write("G0 Y10\n".encode('utf-8'))
        line = ser.readline().decode('utf-8').rstrip()
        print("Reply from ESP: "+line)
        time.sleep(1)
        ser.write("G0 Y-10\n".encode('utf-8'))
        time.sleep(1)
        line = ser.readline().decode('utf-8').rstrip()
        print("Reply from ESP: "+line)

