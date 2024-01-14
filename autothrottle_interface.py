print ("Hello AutoThrottle")

import serial
import time
ser = serial.Serial("COM3", 38400, timeout=1)
# h = 95
# i = 22
#Can we do read/write with the same one?
for i in range(0, 100):
    print("write")
    ser.write(b"hello from COM 3")
    print("read")
    print(ser.read(5))

print("done")
# time.sleep(.1)

# # Read line   
# while True:
#     # Send character 'S' to start the program
    

# print("Done")