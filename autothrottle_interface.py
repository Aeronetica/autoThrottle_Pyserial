print ("Hello AutoThrottle")

import serial
import time
ser3 = serial.Serial("COM3", 38400, timeout=1)
ser4 = serial.Serial("COM4", 38400, timeout=1)
# h = 95
# i = 22
#Can we do read/write with the same one?
for i in range(0, 100):
    ser3.write(b"hello from COM 3")
    ser4.write(b"hello from COM 4")
    print("COM3: " + str(ser3.read(100)))
    print("COM4: " + str(ser4.read(100)))
    time.sleep(1)
print("done")
# time.sleep(.1)

# # Read line   
# while True:
#     # Send character 'S' to start the program
    

# print("Done")