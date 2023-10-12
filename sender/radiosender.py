import struct
from shared.utilities import calculate_crc
from shared.protocol_ids import Sender_ID, Chase_Data_ID

NUM_BYTES_IN_WORD = 4


# turn into class
class BssrProtocolSender:

    MAX_PHRASE_LENGTH = 11

    # Packet constants
    START_BYTE = 165
    NUM_CRC_BYTES = 0x4

    def __init__(self, connection):
        self.connection = connection

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

    def _eco_sender(self, eco_on):
        payload = [Chase_Data_ID.CHASE_ECO_MODE_ID, eco_on, 0x00, 0x00]
        self.send_serial(payload)

    def _cruise_PI_sender(self, k_p: float, k_i: float, k_d: float):
        payload = [
            Chase_Data_ID.CHASE_CRUISE_PI_GAIN_ID, int(k_p != None), int(k_i != None), int(k_d != None),
            0, 0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0,
        ]
        GAIN_SCALE_FACTOR = 100000

        if k_p != None:
            k_p = int(GAIN_SCALE_FACTOR*k_p)
            byte_array = list(struct.pack('I', k_p))
            for i in range(4):
                payload[4+i] = byte_array[3-i]

        if k_i != None:
            k_i = int(GAIN_SCALE_FACTOR*k_i)
            byte_array = list(struct.pack('I', k_i))
            for i in range(4):
                payload[8+i] = byte_array[3-i]

        if k_d != None:
            k_d = int(GAIN_SCALE_FACTOR*k_d)
            byte_array = list(struct.pack('I', k_d))
            for i in range(4):
                payload[12+i] = byte_array[3-i]
        
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

    def eco_on_sender(self):
        print("ECO On")
        self._eco_sender(0x01)
    
    def eco_off_sender(self):
        print("ECO Off")
        self._eco_sender(0x00)

    def cruise_PI_KP_sender(self, k_p):
        self._cruise_PI_sender(k_p, None, None)
    
    def cruise_PI_KI_sender(self, k_i):
        self._cruise_PI_sender(None, k_i, None)

    def cruise_PI_KD_sender(self, k_d):
        self._cruise_PI_sender(None, None, k_d)