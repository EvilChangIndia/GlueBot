#!/usr/bin/env python3
import serial
import time
if __name__ == '__main__':
    print("trying to connect to ESP at /dev/ttyUSB0")
    esp = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    esp.reset_input_buffer()
    line="$G\n"
    esp.write(line.encode('utf-8'))
    line="$X\n"
    esp.write(line.encode('utf-8'))
    while True:
        espReply=""
        line=input("enter cmd to send: ")
        esp.write(line.encode('utf-8'))
        while espReply =="": 
            espReply = esp.readline().decode('utf-8').rstrip()
        print("Reply from ESP: "+espReply)
