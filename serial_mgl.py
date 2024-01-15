print("Hello AutoThrottle")

import serial
import time



#ser3 = serial.Serial("COM6", 38400, timeout=1)
# set_servo_number_efis_to_servo(ser3, 1)
# time.sleep(1)
# read_servo_ack_from_servo_to_efis(ser3)
ser3 = None
Mode = 1 # mode==0 is engaged, 1 is armed. 2 is standby
set_servo_position = 10
for i in range(10):  #about 5 seconds per 10
    if Mode == 0:   #engaged
        send_servo_position_message_from_efis_to_servo(ser3, set_servo_position)
        time.sleep(.05)
        return_dict = read_servo_ack_from_servo_to_efis(ser3)
        pad = 5
        if(set_servo_position-pad < return_dict["position"] < set_servo_position+pad):
            Mode = 1 #goto arm
        if(return_dict["slipping"] == 1):
            Mode = 2 #goto standby
        print("Engaged")
        time.sleep(.25)
    elif Mode == 1:  #armed
        send_servo_position_message_from_efis_to_servo(ser3, -1)
        time.sleep(.05)
        return_dict = read_servo_ack_from_servo_to_efis(ser3)
        if(not (set_servo_position-pad < return_dict["position"] < set_servo_position+pad)):
            Mode = 0  #engage
        if(return_dict["slipping"] == 1):
            Mode = 2 #goto standby
        print("Armed")
        time.sleep(.25)
    elif Mode == 2: #standby
        print("Standby")
        time.sleep(.4)
    else:
        print("Error")


time.sleep(.1)
send_servo_position_message_from_efis_to_servo(ser3, -1)
time.sleep(.1)
read_servo_ack_from_servo_to_efis(ser3)

