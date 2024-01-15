print("Hello AutoThrottle")

import time

import serial


def andbytes(abytes, bbytes):
    return bytes([a & b for a, b in zip(abytes[::-1], bbytes[::-1])][::-1])


ser3 = serial.Serial("COM3", 38400, timeout=1)
ser4 = serial.Serial("COM4", 38400, timeout=1)
# h = 95
# i = 22
# Can we do read/write with the same one?
for i in range(0, 2):
    some_int = int("0x0216", 16)
    other_int = 550
    ser3.write(some_int.to_bytes(2, byteorder="big"))
    ser4.write(other_int.to_bytes(2, byteorder="big"))
    r_three = ser3.read(100)
    r_four = ser4.read(100)
    f_four_mod = int(r_four.hex(), 16) & int("0xFF0", 0)
    print("COM3: " + str(int(r_three.hex(), 16)))
    print("COM4: pre: " + str(r_four.hex()) + " post: " + str(hex(f_four_mod)))
    time.sleep(1)
print("done")

# time.sleep(.1)

# # Read line
# while True:
#     # Send character 'S' to start the program


# print("Done")
