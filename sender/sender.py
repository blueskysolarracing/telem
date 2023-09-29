import time
import numpy as np
from lib.utilities import calculate_crc
from lib.protocol_ids import Sender_ID, Chase_Data_ID

NUM_BYTES_IN_WORD = 4


# turn into class
class BssrProtocolSender:

    MAX_PHRASE_LENGTH = 11

    # Packet constants
    START_BYTE = 165
    NUM_CRC_BYTES = 0x4

    def __init__(self, connection):
        self.connection = connection

    @classmethod
    def send_serial(self, payload):
        "Send bytes from serial port to UART Hub"

        # packet = [START_BYTE, PAYLOAD_LENGTH, CHASE_SENDER_ID, self.sequence_num] + payload
        packet = [self.START_BYTE, len(payload), Sender_ID.CHASE_ID, 0] + payload

        # CRC = utilities.calculate_crc(packet, PAYLOAD_LENGTH)
        CRC = calculate_crc(packet, len(payload), use_numpy=False)
        print(f"CRC: {CRC}")
        packet += CRC

        print("Sent packet: ", bytes(packet).hex())
        print("Packet length: ", len(packet))

        self.connection.write(bytearray(packet))
    
    def _vfm_sender(self, vmf_state):
        payload = [Chase_Data_ID.CHASE_VMF_ID, vmf_state, 0x00, 0x00]
        self.send_serial(payload)

    def phrase_sender(self, phrase):
        print(f"Sending Message: {phrase}")

        if len(phrase) < self.MAX_PHRASE_LENGTH:
            new_phrase = phrase + ' ' * (self.MAX_PHRASE_LENGTH -len(phrase))
        else: 
            new_phrase = phrase
        
        payload = bytes(new_phrase, 'utf-8').hex()
        # turn payload into list of bytes
        payload = [Chase_Data_ID.CHASE_MESSAGE_ID] + [int(payload[i:i+2], 16) for i in range(0, len(payload), 2)]
        print(f"ID and word encoding: {payload}")
        self.send_serial(payload)

    def vfm_up_sender(self):
        print("VFM Up")
        self._vfm_sender(0x01)

    def vfm_down_sender(self):
        print("VFM Down")
        self._vfm_sender(0x00)

    def eco_sender(self, eco_on: bool):
        print(f"eco set to: {eco_on}")
        payload = [Chase_Data_ID.CHASE_ECO_MODE_ID, 0x01 if eco_on else 0x00 , 0x00, 0x00]
        self.send_serial(payload)