print ("Hello AutoThrottle")

import serial
import time

def andbytes(abytes, bbytes):
    return bytes([a & b for a, b in zip(abytes[::-1], bbytes[::-1])][::-1])


ser3 = serial.Serial("COM3", 38400, timeout=1)
ser4 = serial.Serial("COM4", 38400, timeout=1)
# h = 95
# i = 22
#Can we do read/write with the same one?
for i in range(0, 2):
    some_int = 28
    other_int = 550
    ser3.write(some_int.to_bytes(2, byteorder='big'))
    ser4.write(other_int.to_bytes(2, byteorder='big'))
    r_three = ser3.read(100)
    r_four = ser4.read(100)
    print("COM3: " + str(int(r_three.hex(), 16)))
    print("COM4: " + str(int(r_four.hex(), 16)))
    time.sleep(1)
print("done")

# time.sleep(.1)

# # Read line   
# while True:
#     # Send character 'S' to start the program
    

# print("Done")