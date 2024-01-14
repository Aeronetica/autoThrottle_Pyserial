print ("Hello AutoThrottle")

import serial
import time
ser = serial.Serial("COM3", 38400, timeout=1)
# h = 95
# i = 22
print("write")
ser.write(b"hello")
print("done")
# time.sleep(.1)

# # Read line   
# while True:
#     # Send character 'S' to start the program
    

# print("Done")