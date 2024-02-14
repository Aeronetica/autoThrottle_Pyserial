"""Contains the throttle controller class and the servo states enum used
    by the throttle controller class. The throttle controller class is used to
    control the throttle servo. The throttle servo is a 12V servo that is
    controlled by a serial port."""

import json
import logging
import sys
import time
from enum import Enum

import serial

# in order to use serial, you need to `pip install pySerial``


class ServoStates(Enum):
    """Enum for the different states of the servo"""

    ERROR = -1
    ENGAGED = 0
    ARMED = 1
    STANDBY = 2


class ThrottleController:
    """Throttle Controller class. Used to control the throttle servo"""

    def __init__(self, port_string: str, config_file: str, servo_number: int = 1):
        """Throttle Controller constructor

        Args:
            port_string (str): string containing the port to connect to
            config_file (str): config file to load parameters from. Should be a json file
            servo_number (int, optional): servo number to connect to. Defaults to 1.
        """
        self.port_string = port_string
        self.config_file = config_file
        self.servo_number = servo_number
        self.mode = ServoStates.ARMED
        self.throttle_pad = 5  # clicks
        self.message_dict = {}
        self.initialize()
        self.setup_logging()
        self.open_port()
        self.initialize_servo()

    def initialize(self):
        """Initialize the throttle controller by loading parameters from the json
        config file"""
        with open(self.config_file, encoding="utf_8") as fp:
            params = json.load(fp)
        self.full_position = params["full_position"]
        self.over_torque = params["over_torque"]

    def setup_logging(self):
        """Setup the logging for the throttle controller. Logs to a file and to the console"""
        self.logger = logging.getLogger("ThrottleController")
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler("throttle_controller.log")
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def open_port(self) -> bool:
        """Open the serial port to the servo and return if it was successful or not"""
        try:
            self.port = serial.Serial(self.port_string, 38400, timeout=1)
        except Exception as e:
            self.logger.error(
                "Could not open port %s, because of exception %s", self.port_string, e
            )
            sys.exit(-1)
        if self.port is None:
            self.logger.error("Port not open")
            sys.exit(-2)
        else:
            self.logger.error("Port open")

    def initialize_servo(self):
        """Initialize the servo by setting the servo number"""

        self.set_servo_number_efis_to_servo()
        ack = self.port.read(100)  # Large Number
        self.logger.debug([hex(i) for i in ack])

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
        """Set the servo number from the EFIS to the servo"""

        start_mesgs = [0xD5, 0x82]
        set_message_length = [6]
        set_servo_mesgs = [0x00, 0x00, 0xAA, 0x55]
        set_servo_number = 1
        set_servo_mesgs.append(set_servo_number & 0xFF)  # Set servo to number
        set_servo_mesgs.append(
            (set_servo_number ^ 0xFF) & 0xFF
        )  # Set servo message length
        # calculate xor of all bytes in set_servo_mesgs
        chks1 = [self.calculate_checksum1(set_servo_mesgs, seed=0xAA)]
        chks2 = [self.calculate_checksum2(set_servo_mesgs, seed=0x55)]
        whole_message = (
            start_mesgs + set_message_length + set_servo_mesgs + chks1 + chks2
        )
        self.logger.debug("Send Message: ")
        self.logger.debug([hex(i) for i in whole_message])
        self.port.write(bytes(whole_message))

    def send_servo_position_message_from_efis_to_servo(self, position: int):
        """send the servo position message from the EFIS to the servo

        Args:
            position (int): the position to send to the servo. if -1 then just poll the position
        """
        start_mesgs = [0xD5, 0x82]
        set_message_length = [15]
        set_message_header = [0x01, 0x00]
        set_frespond = [0x01]
        if position == -1:
            self.logger.info("**** Not commanding servo position, just listening")
            set_options_1 = [0x00]
            tgt_position = 0x00.to_bytes(2, byteorder="little")
        else:
            self.logger.info("**** Commanding servo position to %d", position)
            set_options_1 = [
                0x71  # Torque of 7 and engage and reset torque measurement
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
        chks1 = [self.calculate_checksum1(set_servo_mesg, seed=0xAA)]
        chks2 = [self.calculate_checksum2(set_servo_mesg, seed=0x55)]
        whole_message = (
            start_mesgs + set_message_length + set_servo_mesg + chks1 + chks2
        )

        self.logger.debug("Send Message: ")
        self.logger.debug([hex(i) for i in whole_message])
        self.port.write(bytes(whole_message))

    def read_servo_ack_from_servo_to_efis(self):
        """Read the servo ack message from the servo to the EFIS"""
        message_dict = {}
        ack_size = 12

        ack = self.port.read(ack_size)
        ack_bytes = list(ack)

        if len(ack) < 12:
            return {}

        self.message_dict["enganged"] = ack_bytes[5] & 0x01
        self.message_dict["slipping"] = ack_bytes[5] & 0x02
        self.message_dict["voltage_alarm"] = ack_bytes[5] & 0x03
        self.message_dict["position"] = ack_bytes[7] * 256 + ack_bytes[6]
        self.message_dict["voltage"] = ack_bytes[8]
        self.message_dict["torque"] = ack_bytes[9]

        self.message_dict["ack_length"] = len(ack_bytes)
        self.logger.debug(
            "Servo position: %d - Servo torque %d",
            self.message_dict["position"],
            self.message_dict["torque"],
        )
        self.logger.debug("Ack: ")
        self.logger.debug([hex(i) for i in ack])

        return message_dict

    def command_servo(self, position: int):
        """Command the servo to a position

        Args:
            position (int): position to command the servo to
        """
        self.send_servo_position_message_from_efis_to_servo(position)
        time.sleep(0.05)
        return self.read_servo_ack_from_servo_to_efis()

    def run(self):
        """Run a step of the throttle controller"""
        if self.mode == ServoStates.ERROR:  # error
            self.logger.error("General Servo Error...")
            return False

        # Normal Operation
        if self.mode == ServoStates.ENGAGED:  # engaged
            return_dict = self.command_servo(self.full_position)
            if not return_dict:
                self.logger.error("Serial Port not open")
                self.mode = ServoStates.ERROR
                return False
            if (
                self.full_position - self.throttle_pad
                < return_dict["position"]
                < self.full_position + self.throttle_pad
            ):
                self.mode = ServoStates.ARMED  # goto arm
            if return_dict["slipping"] == 1:
                self.mode = ServoStates.STANDBY  # goto standby
            self.logger.debug(
                "Servo Engaged to set position %d and torque %d and voltage %d",
                self.full_position,
                return_dict["torque"],
                return_dict["voltage"],
            )
            time.sleep(0.4)
        elif self.mode == ServoStates.ARMED:  # armed
            return_dict = self.command_servo(-1)
            if not return_dict:
                self.logger.error("Port not open")
                self.mode = ServoStates.ERROR
                return False
            if not (
                self.full_position - self.throttle_pad
                < return_dict["position"]
                < self.full_position + self.throttle_pad
            ):
                self.mode = ServoStates.ENGAGED  # engage
            if return_dict["slipping"] == 1:
                self.mode = ServoStates.STANDBY  # goto standby
            self.logger.info(
                "Servo ARMED with set position %d", return_dict["position"]
            )
            time.sleep(0.4)
        elif self.mode == ServoStates.STANDBY:  # standby
            self.logger.info("Servo STANDBY...")
            time.sleep(0.4)
        else:
            self.logger.error("Servo in unknown mode")
            return False
        return True
