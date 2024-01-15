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
    w_fourty_one = bytes.fromhex("41")
    w_twenty_two = bytes.fromhex("F2")
    w_and = andbytes(w_fourty_one, w_twenty_two)
    ser3.write(w_fourty_one)
    ser4.write(w_twenty_two)
    ser3.write(w_and)
    r_four = ser4.read(100)
    r_mod = andbytes(r_four, b'\xF0')
    print("COM3: " + str(ser3.read(100)))
    print("COM4: " + str(r_four.hex()))
    print("COM4: " + str(r_mod.hex()))
    time.sleep(1)
print("done")

# time.sleep(.1)

# # Read line   
# while True:
#     # Send character 'S' to start the program
    

# print("Done")