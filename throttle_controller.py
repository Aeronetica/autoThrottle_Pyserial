import serial
import time
import json
import logging
from enum import Enum

class ServoStates(Enum):
    ERROR = -1
    ENGAGED = 0
    ARMED = 1
    STANDBY = 2
class ThrottleController():
    
    def __init__(self, port_string: str, config_file: str, servo_number: int = 1):
        """Throttle Controller constructor 

        Args:
            port_string (str): string containing the port to connect to
            config_file (str): config file to load parameters from. Should be a json file
        """
        self.port_string = port_string
        self.config_file = config_file
        self.servo_number = servo_number
        self.mode = ServoStates.ARMED
        self.throttle_pad = 5  #clicks
        self.initialize()
        self.setup_logging()
        self.open_port()
        
        
    def initialize(self):
        with open(self.config_file) as fp:
            params = json.load(fp)
        self.full_position = params["full_position"]
        self.over_torque = params["over_torque"]
    
    def setup_logging(self):
        self.logger = logging.getLogger('ThrottleController')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('throttle_controller.log')
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        
    def open_port(self) -> bool:
        try:
            self.port = serial.Serial(self.port_string, 38400, timeout=1)
        except:
            self.port = None
            self.logger.error("Could not open port %s", self.port_string)
    
    def calculate_checksum1(self, mesg_list: list[int], seed: int = 0):
        """Calculate the checksum of an one byte integer array of values

        Args:
            msg (list[int]): list of bytes to send
            seed (int): One byte seed value. Defaults to 0
        """
        checksum = seed
        for i in mesg_list:
            checksum = (checksum + i) & 0xFF
        return checksum


    def calculate_checksum2(self, mesg_list: list[int], seed: int = 0):
        """Calculate the checksum2 of an one byte integer array of values

        Args:
            msg (list[int]): list of bytes to send
            seed (int): One byte seed value. Defaults to 0
        """
        checksum = seed
        for i in mesg_list:
            checksum = checksum ^ i
        return checksum


    def set_servo_number_efis_to_servo(self):
        """Set the servo number using a serial port connected with usb to rs232 cable

        Args:
            serial_port (serial.Serial): Serial port to send message to
            servo_number (int): Servo number to set
        """
        start_mesgs = [0xD5, 0x82]
        set_message_length = [6]
        set_servo_mesgs = [0x00, 0x00, 0xAA, 0x55]
        set_servo_number = 1
        set_servo_mesgs.append(set_servo_number & 0xFF)  # Set servo to number
        set_servo_mesgs.append((set_servo_number ^ 0xFF) & 0xFF)  # Set servo message length
        # calculate xor of all bytes in set_servo_mesgs
        chks1 = [self.calculate_checksum1(set_servo_mesgs, seed=0xAA)]
        chks2 = [self.calculate_checksum2(set_servo_mesgs, seed=0x55)]
        whole_message = start_mesgs + set_message_length + set_servo_mesgs + chks1 + chks2
        print("Send Message: ")
        print([hex(i) for i in whole_message])
        if self.port is not None:
            self.port.write(bytes(whole_message))
        else:
            self.logger.error("Port not open")



    def send_servo_position_message_from_efis_to_servo(
        self, serial_port: serial.Serial, position: int
    ):
        """send the servo position message from the EFIS to the servo

        Args:
            serial_port (serial.Serial): the serial port to send the message to
            position (int): the position to send to the servo. if -1 then just poll the position
        """
        start_mesgs = [0xD5, 0x82]
        set_message_length = [15]
        set_message_header = [0x01, 0x00]
        set_frespond = [0x01]
        if position == -1:
            set_options_1 = [0x00]
            tgt_position = 0x00.to_bytes(2, byteorder="little")
        else:
            set_options_1 = [
                0x01
            ]  # Here we will not reset torque measurement and not set torque
            tgt_position = (position).to_bytes(2, byteorder="little")
        
        tgt_position_send = [tgt_position[0], tgt_position[1]]

        fill_bytes = (0).to_bytes(9, byteorder="little")
        fill_bytes_send = [
            fill_bytes[0],
            fill_bytes[1],
            fill_bytes[2],
            fill_bytes[3],
            fill_bytes[4],
            fill_bytes[5],
            fill_bytes[6],
            fill_bytes[7],
            fill_bytes[8],
        ]
        set_servo_mesg = (
            set_message_header
            + set_frespond
            + set_options_1
            + tgt_position_send
            + fill_bytes_send
        )
        print([hex(i) for i in set_servo_mesg])
        chks1 = [self.calculate_checksum1(set_servo_mesg, seed=0xAA)]
        chks2 = [self.calculate_checksum2(set_servo_mesg, seed=0x55)]
        whole_message = start_mesgs + set_message_length + set_servo_mesg + chks1 + chks2
        print("Send Message: ")
        print([hex(i) for i in whole_message])
        if self.port is not None:
            self.port.write(bytes(whole_message))
        else:
            self.logger.error("Port not open")
        
    def read_servo_ack_from_servo_to_efis(self, serial_port: serial.Serial):
        """Read the servo ack message from the servo to the EFIS

        Args:
            serial_port (serial.Serial): the serial port to read from
        """
        message_dict = {}
        ack_size = 12
        if self.port is not None:
            ack = self.port.read(ack_size)
        else:
            self.logger.error("Port not open")
            return None

        ack_bytes = list(ack)
        message_dict["torque"] = ack_bytes[9]
        message_dict["voltage"] = ack_bytes[8]
        message_dict["Position"] = ack_bytes[7]*256 + ack_bytes[6]
        message_dict["enganged"] = ack_bytes[5] & 0x01
        message_dict["slipping"] = ack_bytes[5] & 0x02
        message_dict["voltage_alarm"] = ack_bytes[5] & 0x03
        message_dict["ack_length"] = len(ack_bytes)
        print("Ack: ")
        print([hex(i) for i in ack])
        
        return message_dict

    def command_servo(self, position: int):
        """Command the servo to a position

        Args:
            position (int): position to command the servo to
        """
        self.send_servo_position_message_from_efis_to_servo(self.port, position)
        time.sleep(.05)
        self.return_dict = self.read_servo_ack_from_servo_to_efis(self.port)
    
    def run(self):
        """Run the throttle controller
        """
        if self.mode == ServoStates.ERROR:  #error
            self.logger.error("Servo in Error Mode")
            time.sleep(.5)
        elif self.mode == ServoStates.ENGAGED:   #engaged
            return_dict = self.command_servo(self.full_position)
            if not return_dict:
                self.logger.error("Port not open")
                self.mode = ServoStates.ERROR
                return
            if(self.full_position-self.throttle_pad < return_dict["position"] < self.full_position+self.throttle_pad):
                Mode = ServoStates.ARMED #goto arm
            if(return_dict["slipping"] == 1):
                Mode = ServoStates.STANDBY #goto standby
            self.logger.info("Servo Engaged to set position %d", self.full_position)
            time.sleep(.4)
        elif Mode == ServoStates.ARMED:  #armed
            return_dict = self.command_servo(-1)
            if not return_dict:
                self.logger.error("Port not open")
                self.mode = ServoStates.ERROR
                return False
            if(not (self.full_position-self.throttle_pad < return_dict["position"] < self.full_position+self.throttle_pad)):
                Mode = ServoStates.ENGAGED  #engage
            if(return_dict["slipping"] == 1):
                Mode = ServoStates.STANDBY #goto standby
            self.logger.info("Servo ARMED with set position %d", return_dict["position"])
            time.sleep(.4)
        elif Mode == ServoStates.STANDBY: #standby
            self.logger.info("Servo STANDBY...")
            time.sleep(.4)
        elif Mode == ServoStates.ERROR: #error
            self.logger.info("Servo Error...")
            time.sleep(1)
            return False
        else:
            self.logger.error("Servo in unknown mode")
            time.sleep(.5)
            return False
        return True

    