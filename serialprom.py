import numpy as np
from prometheus_client import start_http_server, Counter, Gauge
import time
import struct
import telemGui.utilities as utilities
import multiprocessing as mp
import serial

SERIAL_PORT = '/dev/ttyUSB2'

MAX_PAYLOAD_SIZE = 24
MAX_PACKET_SIZE = 32
ESCAPED_BYTE = 90
STARTING_BYTE = 165
NUM_CRC_BYTES = 4

# Sender ID's
BBMB_SENDER_ID = 1
PPTMB_SENDER_ID = 2
MCMB_SENDER_ID = 3
DCMB_SENDER_ID = 4
# chase and bms are not currently being used

# Data ID's
BUS_METRICS = 0
CAR_SPEED = 1
MOTOR_TEMPERATURE = 2
MOTOR_CONTROL = 5
RELAY_STATE = 6
CELL_TEMPERATURE = 7
CELL_VOLTAGE = 8
CELL_SOC = 9
BMS_HEARTBEAT = 10
LIGHT_CONTROL = 3
SIDE_PANEL = 8
CONTROLS = 4
HEARTBEAT = 15

ERROR_WINDOW = 5 # seconds


class Parser:
    def __init__(self, byte_buffer):
        self.byte_buffer = byte_buffer
        start_http_server(8000)

        # Indicate the status of each byte in a packet
        self.escaped_received = False
        self.started_received = False
        self.length_received = False
        self.sender_received = False
        self.sequence_received = False
        self.data_id_received = False
        self.payload_received = False
        self.crc_received = False
        self.packet_complete = False
        self.packet_corrupt = False

        # Packet values
        self.sender = -1
        self.payload_length = -1
        self.data_id = -1
        self.payload = np.zeros(MAX_PAYLOAD_SIZE, dtype=np.uint8)
        self.packet = np.zeros(MAX_PACKET_SIZE, dtype=np.uint8)
        self.packets_processed = 0
        self.crc = np.zeros(NUM_CRC_BYTES, dtype=np.uint8)
        self.sequence_bytes = {
            1: -1, # BBMB
            2: -1, # PPTMB
            3: -1, # MCMB
            4: -1, # DCMB
            5: -1, # Not Used
            6: -1, # Not Used
        }
        self.allBytes = []
        self.valid_crc = False

        # State Variables  
        self.packet_index = 0
        self.packet_length = 0

        # Radio health
        self.num_packets_received = 0
        self.num_packets_corrupted = 0

        self.reference_time = time.time()


        # Prometheus metrics

        # BUS METRICS
        self.bbmb_bus_metrics_voltage_gauge = Gauge("bbmb_bus_voltage", "BBMB Bus Voltage")
        self.bbmb_bus_metrics_current_gauge = Gauge("bbmb_bus_current", "BBMB Bus Current")

        self.pptmb_bus_metrics_voltage_gauge = Gauge("pptmb_bus_voltage", "PPTMB Bus Voltage")
        self.pptmb_bus_metrics_current_gauge = Gauge("pptmb_bus_current", "PPTMB Bus Current")

        self.mcmb_bus_metrics_voltage_gauge = Gauge("mcmb_bus_voltage", "MCMB Bus Voltage")
        self.mcmb_bus_metrics_current_gauge = Gauge("mcmb_bus_current", "MCMB Bus Current")


        # MCMB
        self.mcmb_car_speed_gauge = Gauge("mcmb_car_speed", "MCMB Car Speed")
        self.mcmb_motor_temperature = Gauge("mcmb_motor_temperature", "MCMB Motor Temperature")

        # Heartbeats
        self.bbmb_heartbeat = Gauge("bbmb_heartbeat", "BBMB Heartbeat")
        self.pptmb_heartbeat = Gauge("pptmb_heartbeat", "PPTMB Heartbeat")
        self.mcmb_heartbeat = Gauge("mcmb_heartbeat", "MCMB Heartbeat")
        self.dcmb_heartbeat = Gauge("dcmb_heartbeat", "DCMB Heartbeat")

    def run(self):
        """
        Read from the queue of bytes
        """    
        count = 0
        while True:
            count += 1

            byte = self.byte_buffer.get()[0]

           # Escaped byte 0x5a - 90 
            if byte == ESCAPED_BYTE and self.escaped_received != True:
                self.escaped_received = True
            # Starting byte
            elif byte == STARTING_BYTE and self.started_received != True:
                self.started_received = True
                self.packet[self.packet_index] = byte
                self.packet_index += 1
            # length byte
            elif self.started_received and self.length_received != True:
                if self.escaped_received:
                    self.escaped_received = False
            
                self.length_received = True
                self.payload_length = byte

                self.packet[self.packet_index] = byte
                self.packet_index += 1

                # If the payload length exceeds the maximum size, drop the byte and start the packet again
                if (self.payload_length > 24):
                    self.reset_loop_variables()

            # sender byte (board)
            elif self.started_received and self.length_received and self.sender_received != True:
                if self.escaped_received:
                    self.escaped_received = False

                self.sender_received = True
                self.sender = byte
                self.packet[self.packet_index] = byte
                self.packet_index += 1

                # If the sender byte is invalid, drop the byte and start again
                if (self.sender < 1 or self.sender > 6):
                    self.reset_loop_variables()

            # sequence byte
            elif self.started_received and self.length_received and self.sender_received and self.sequence_received != True:
                if self.escaped_received:
                    self.escaped_received = False
                
                self.sequence_received = True
                self.packet[self.packet_index] = byte

                last_sequence_byte = self.sequence_bytes[self.sender]
                dropped_packets = byte - last_sequence_byte if last_sequence_byte != -1 and byte - last_sequence_byte > 1 else 0
                self.num_packets_corrupted += dropped_packets 
                self.sequence_bytes[self.sender] = byte
                self.packet_index += 1
            # data id byte - also needs to go in payload array
            elif self.started_received and self.length_received and self.sender_received and self.sequence_received and self.data_id_received != True:
                if self.escaped_received:
                    self.escaped_received = False

                self.data_id_received = True
                self.data_id = byte
                self.packet[self.packet_index] = byte
                self.payload[self.payload_length - 1] = byte
                self.packet_index += 1

                # If the data id goes past 15, drop the byte and start again
                if (self.data_id > 15):
                    self.reset_loop_variables()

            # payload bytes
            elif self.started_received and self.length_received and self.sender_received and self.sequence_received and self.data_id_received and self.payload_received != True:
                idx = 1

                while idx < self.payload_length:
                    # escaped byte
                    if byte == ESCAPED_BYTE and self.escaped_received != True:
                        self.escaped_received = True
                        byte = self.byte_buffer.get()[0]
                        continue # don't increment the index properties
                    elif self.escaped_received:
                        self.escaped_received = False

                    self.packet[self.packet_index] = byte

                    # We store it in reverse order to swap the endians
                    self.payload[self.payload_length - idx - 1] = byte

                    idx += 1
                    self.packet_index += 1

                    if idx < self.payload_length:
                        byte = self.byte_buffer.get()[0]
                
                self.payload_received = True
            
            # crc bytes
            elif self.started_received and self.length_received and self.sender_received and self.sequence_received and self.data_id_received and self.payload_received and self.crc_received != True:
                idx = 0

                while idx < NUM_CRC_BYTES:
                    # Escaped byte
                    if byte == ESCAPED_BYTE and self.escaped_received != True:
                        self.escaped_received = True
                        byte = self.byte_buffer.get()[0]
                        continue # don't increment the index properties
                    elif self.escaped_received:
                        self.escaped_received = False

                    self.packet[self.packet_index] = byte
                    self.crc[idx] = byte
                    idx += 1
                    self.packet_index += 1   

                    if idx < NUM_CRC_BYTES:
                        byte = self.byte_buffer.get()[0]

                self.packet_complete = True

            if self.packet_complete:
                # process crc
                calculated_crc = utilities.calculate_crc(self.packet, self.payload_length)
                crc_bytes = self.packet[self.packet_index-4:self.packet_index]
                if np.array_equal(calculated_crc, crc_bytes):
                    self.valid_crc = True
                    self.num_packets_received += 1
                    self.extract_data()
                else:
                    self.num_packets_corrupted += 1

                self.reset_loop_variables()

            current_time = time.time()
            if (current_time - self.reference_time > ERROR_WINDOW):
                self.reference_time = current_time
                # Reset sender variables
                self.sequence_bytes = {
                    1: -1, # BBMB
                    2: -1, # PPTMB
                    3: -1, # MCMB
                    4: -1, # DCMB
                    5: -1, # Not Used
                    6: -1, # Not Used
                }
                self.num_packets_corrupted = 0
                self.num_packets_received = 0 

    def reset_loop_variables(self):
        """
        Reset loop variables in order to construct the next packet
        """
        self.escaped_received = False
        self.started_received = False
        self.length_received = False
        self.sender_received = False
        self.sequence_received = False
        self.data_id_received = False
        self.payload_received = False
        self.crc_received = False
        self.packet_complete = False
        self.packet_corrupt = False
        self.names_to_change = []
        self.values_to_change = []

        self.sender = -1
        self.payload_length = -1
        self.data_id = -1
        self.payload = np.zeros(MAX_PAYLOAD_SIZE, dtype=np.uint8)
        self.packet = np.zeros(MAX_PACKET_SIZE, dtype=np.uint8)
        self.crc = np.zeros(NUM_CRC_BYTES, dtype=np.uint8)
        self.packet_index = 0
        self.valid_crc = False

    def extract_data(self):
        """
        Parse the packet stored in self.packet and update the gui
        """      

        # BBMB
        if self.sender == BBMB_SENDER_ID:
            if self.data_id == BUS_METRICS:
                self.bbmb_bus_metrics_current_gauge.set(struct.unpack('f', self.payload[0:4])[0])
                self.bbmb_bus_metrics_voltage_gauge.set(struct.unpack('f', self.payload[4:8])[0])
            elif self.data_id == CELL_TEMPERATURE:
                self.bms_cell_temp_module_id = self.payload[14]
            elif self.data_id == HEARTBEAT:
                self.bbmb_heartbeat.set(self.payload[2])

        elif self.sender == PPTMB_SENDER_ID:
            if self.data_id == BUS_METRICS:
                self.pptmb_bus_metrics_current_gauge.set(struct.unpack('f', self.payload[0:4])[0])
                self.pptmb_bus_metrics_voltage_gauge.set(struct.unpack('f', self.payload[4:8])[0])
            elif self.data_id == HEARTBEAT:
                self.pptmb_heartbeat.set(self.payload[2])

        elif self.sender == MCMB_SENDER_ID:
            if self.data_id == BUS_METRICS:
                self.mcmb_bus_metrics_current_gauge.set(struct.unpack('f', self.payload[0:4])[0])
                self.mcmb_bus_metrics_voltage_gauge.set(struct.unpack('f', self.payload[4:8])[0])
            elif self.data_id == CAR_SPEED:
                self.mcmb_car_speed_gauge.set(self.payload[3])
            elif self.data_id == MOTOR_TEMPERATURE:
                self.mcmb_motor_temperature.set(struct.unpack('f', self.payload[0:4])[0])
            elif self.data_id == HEARTBEAT:
                self.mcmb_heartbeat.set(self.payload[2])

        elif self.sender == DCMB_SENDER_ID:
            if self.data_id == HEARTBEAT:
                self.dcmb_heartbeat.set(self.payload[2])
                

            

def start_parser(byte_buffer: mp.Queue):
    """Start the parser"""
    parser = Parser(byte_buffer)
    parser.run()

def read_serial(byte_buffer: mp.Queue):
    """Read from serial and write to buffer"""
    ser = serial.Serial(SERIAL_PORT, 115200)
    while True:
        try:
            byte = ser.read(1)
            byte_buffer.put(byte)
        finally:
            continue

def main():
    """
    Run the parser
    """
    byte_buffer = mp.Queue()
    serial_proc = mp.Process(target=read_serial, args=(byte_buffer,))
    serial_proc.start()
    serial_parser = mp.Process(target=start_parser, args=(byte_buffer,))
    serial_parser.start()




if __name__ == "__main__":
    main()
