"""
Utility functions
"""

import numpy as np
from datetime import datetime
import pandas as pd

NUM_BYTES_IN_WORD = 4

def calculate_crc(crc_bytes, payload_length):
    """
    Calculate the crc from a 4-byte aligned array
    crc_bytes: numpy array of bytes
    payload_length: How many bytes make up the payload
    """
    
    num_elements = crc_bytes[0:4+payload_length].size
    if (num_elements % NUM_BYTES_IN_WORD != 0):
        return np.zeros(4)

    num_words = int(num_elements / NUM_BYTES_IN_WORD)

    # swap endians
    uint32_value = [((crc_bytes[i]) + (crc_bytes[i+1] << 8) + (crc_bytes[i+2] << 16) + (crc_bytes[i+3] << 24)) for i in range(0, num_elements, 4)]

    raw = crc32Block(0xFFFFFFFF, num_words, uint32_value)
    raw = raw ^ 0xFFFFFFFF
    
    crc = np.array([(raw >> 24) & 0xFF, (raw >> 16) & 0xFF, (raw >> 8) & 0xFF, raw & 0xFF])
    return crc

def crc32Block(crc, size, data):
    for i in range(size):
        crc = crc32(crc, data[i])
        
    return crc

def crc32(crc, data):
    crc = crc ^ data
    for i in range(32):
        if crc & 0x80000000:
            crc = (crc << 1) ^ 0x04C11DB7
        else:
            crc = crc << 1

    return crc

SQL_DATABASE_INDICES = {
    "BBMB Bus Metrics Voltage": 0,
    "BBMB Bus Metrics Current": 1,
    "PPTMB Bus Metrics Voltage": 9,
    "PPTMB Bus Metrics Current": 10,
    "MCMB Bus Metrics Voltage": 15,
    "MCMB Bus Metrics Current": 16,
    "Array Power": [9, 10], # P = IV
    "Module 0 Cell Temperature": [51, 52, 53],
    "Module 1 Cell Temperature": [54, 55, 56],
    "Module 2 Cell Temperature": [57, 58, 59],
    "Module 3 Cell Temperature": [61, 61, 62],
    "Module 4 Cell Temperature": [63, 64, 65],
    "Module 5 Cell Temperature": [66, 67, 68],
    "Module 0 Cell Voltage": [70, 71, 72, 73, 74],
    "Module 1 Cell Voltage": [75, 76, 77, 78, 79],
    "Module 2 Cell Voltage": [80, 81, 82, 83, 84],
    "Module 3 Cell Voltage": [85, 86, 87, 88, 89],
    "Module 4 Cell Voltage": [90, 91, 92, 93, 94],
    "Module 5 Cell Voltage": [95, 96, 97, 98, 99],
    "Module 0 Cell SOC": [101, 102, 103, 104, 105],
    "Module 1 Cell SOC": [106, 107, 108, 109, 110],
    "Module 2 Cell SOC": [111, 112, 113, 114, 115],
    "Module 3 Cell SOC": [116, 117, 118, 119, 120],
    "Module 4 Cell SOC": [121, 122, 123, 124, 125],
    "Module 5 Cell SOC": [126, 127, 128, 129, 130],
    "Timestamp": 133
}

def create_packets_csv():
    """
    Create the packets csv with only the header row
    """
    df = pd.DataFrame(columns=[
        "BBMB Bus Metrics Voltage",
        "BBMB Bus Metrics Current",
        "BBMB Battery Health State",
        "BBMB Battery Relay State",
        "BBMB Array Relay State",
        "BBMB Fault Type",
        "BBMB Faulted Cell",
        "BBMB Faulted Thermister",
        "BBMB Heartbeat",
        "PPTMB Bus Metrics Voltage",
        "PPTMB Bus Metrics Current",
        "PPTMB Battery Health State",
        "PPTMB Battery Relay State",
        "PPTMB Array Relay State",
        "PPTMB Heartbeat",
        "MCMB Bus Metrics Voltage",
        "MCMB Bus Metrics Current",
        "MCMB Car Speed",
        "MCMB Motor Temperature",
        "MCMB Heartbeat",
        "DCMB Cruise",
        "DCMB Horn",
        "DCMB Right Indicator",
        "DCMB Left Indicator",
        "DCMB Motor Control State",
        "DCMB VFM Position",
        "DCMB Target Speed",
        "DCMB Target Power",
        "DCMB Battery Health State",
        "DCMB Battery Relay State",
        "DCMB Array Relay State",
        "DCMB Fault Type",
        "DCMB Faulted Cell",
        "DCMB Faulted Thermister",
        "DCMB Camera",
        "DCMB Fwd/Rev",
        "DCMB Fan",
        "DCMB Aux2",
        "DCMB Aux1",
        "DCMB Aux0",
        "DCMB Array",
        "DCMB Empty",
        "DCMB Start/Stop",
        "DCMB Fault Indicator",
        "DCMB Hazard Lights",
        "DCMB Brake Lights",
        "DCMB DRL",
        "DCMB Indicator",
        "DCMB Left/Right Indicator",
        "DCMB Heartbeat",
        "BMS Temperature Module ID",
        "Module 0 Cell Temperature 0",
        "Module 0 Cell Temperature 1",
        "Module 0 Cell Temperature 2",
        "Module 1 Cell Temperature 0",
        "Module 1 Cell Temperature 1",
        "Module 1 Cell Temperature 2",
        "Module 2 Cell Temperature 0",
        "Module 2 Cell Temperature 1",
        "Module 2 Cell Temperature 2",
        "Module 3 Cell Temperature 0",
        "Module 3 Cell Temperature 1",
        "Module 3 Cell Temperature 2",
        "Module 4 Cell Temperature 0",
        "Module 4 Cell Temperature 1",
        "Module 4 Cell Temperature 2",
        "Module 5 Cell Temperature 0",
        "Module 5 Cell Temperature 1",
        "Module 5 Cell Temperature 2",
        "BMS Voltage Module ID",
        "Module 0 Cell Voltage 0",
        "Module 0 Cell Voltage 1",
        "Module 0 Cell Voltage 2",
        "Module 0 Cell Voltage 3",
        "Module 0 Cell Voltage 4",
        "Module 1 Cell Voltage 0",
        "Module 1 Cell Voltage 1",
        "Module 1 Cell Voltage 2",
        "Module 1 Cell Voltage 3",
        "Module 1 Cell Voltage 4",
        "Module 2 Cell Voltage 0",
        "Module 2 Cell Voltage 1",
        "Module 2 Cell Voltage 2",
        "Module 2 Cell Voltage 3",
        "Module 2 Cell Voltage 4",
        "Module 3 Cell Voltage 0",
        "Module 3 Cell Voltage 1",
        "Module 3 Cell Voltage 2",
        "Module 3 Cell Voltage 3",
        "Module 3 Cell Voltage 4",
        "Module 4 Cell Voltage 0",
        "Module 4 Cell Voltage 1",
        "Module 4 Cell Voltage 2",
        "Module 4 Cell Voltage 3",
        "Module 4 Cell Voltage 4",
        "Module 5 Cell Voltage 0",
        "Module 5 Cell Voltage 1",
        "Module 5 Cell Voltage 2",
        "Module 5 Cell Voltage 3",
        "Module 5 Cell Voltage 4",
        "BMS Cell SOC Module ID",
        "Module 0 Cell SOC 0",
        "Module 0 Cell SOC 1",
        "Module 0 Cell SOC 2",
        "Module 0 Cell SOC 3",
        "Module 0 Cell SOC 4",
        "Module 1 Cell SOC 0",
        "Module 1 Cell SOC 1",
        "Module 1 Cell SOC 2",
        "Module 1 Cell SOC 3",
        "Module 1 Cell SOC 4",
        "Module 2 Cell SOC 0",
        "Module 2 Cell SOC 1",
        "Module 2 Cell SOC 2",
        "Module 2 Cell SOC 3",
        "Module 2 Cell SOC 4",
        "Module 3 Cell SOC 0",
        "Module 3 Cell SOC 1",
        "Module 3 Cell SOC 2",
        "Module 3 Cell SOC 3",
        "Module 3 Cell SOC 4",
        "Module 4 Cell SOC 0",
        "Module 4 Cell SOC 1",
        "Module 4 Cell SOC 2",
        "Module 4 Cell SOC 3",
        "Module 4 Cell SOC 4",
        "Module 5 Cell SOC 0",
        "Module 5 Cell SOC 1",
        "Module 5 Cell SOC 2",
        "Module 5 Cell SOC 3",
        "Module 5 Cell SOC 4",
        "BMS Heartbeat",
        "Valid CRC",
        "Timestamp"
    ])
    curr_time = str(datetime.now()).replace(" ", "_").replace(":","-")

    df.to_csv(f"./{curr_time}_Packets.csv", index=False)

    return f"{curr_time}_Packets.csv"

def setup_database_strings():
    datas = [
        "BBMB_Bus_Metrics_Voltage",
        "BBMB_Bus_Metrics_Current",
        "BBMB_Battery_Health_State",
        "BBMB_Battery_Relay_State",
        "BBMB_Array_Relay_State",
        "BBMB_Fault_Type",
        "BBMB_Faulted_Cell",
        "BBMB_Faulted_Thermister",
        "BBMB_Heartbeat",
        "PPTMB_Bus_Metrics_Voltage",
        "PPTMB_Bus_Metrics_Current",
        "PPTMB_Battery_Health_State",
        "PPTMB_Battery_Relay_State",
        "PPTMB_Array_Relay_State",
        "PPTMB_Heartbeat",
        "MCMB_Bus_Metrics_Voltage",
        "MCMB_Bus_Metrics_Current",
        "MCMB_Car_Speed",
        "MCMB_Motor_Temperature",
        "MCMB_Heartbeat",
        "DCMB_Cruise",
        "DCMB_Horn",
        "DCMB_Right_Indicator",
        "DCMB_Left_Indicator",
        "DCMB_Motor_Control_State",
        "DCMB_VFM_Position",
        "DCMB_Target_Speed",
        "DCMB_Target_Power",
        "DCMB_Battery_Health_State",
        "DCMB_Battery_Relay_State",
        "DCMB_Array_Relay_State",
        "DCMB_Fault_Type",
        "DCMB_Faulted_Cell",
        "DCMB_Faulted_Thermister",
        "DCMB_Camera",
        "DCMB_Fwd_Rev",
        "DCMB_Fan",
        "DCMB_Aux2",
        "DCMB_Aux1",
        "DCMB_Aux0",
        "DCMB_Array",
        "DCMB_Empty",
        "DCMB_Start_Stop",
        "DCMB_Fault_Indicator",
        "DCMB_Hazard_Lights",
        "DCMB_Brake_Lights",
        "DCMB_DRL",
        "DCMB_Indicator",
        "DCMB_Left_Right_Indicator",
        "DCMB_Heartbeat",
        "BMS_Temperature_Module_ID",
        "Module_0_Cell_Temperature_0",
        "Module_0_Cell_Temperature_1",
        "Module_0_Cell_Temperature_2",
        "Module_1_Cell_Temperature_0",
        "Module_1_Cell_Temperature_1",
        "Module_1_Cell_Temperature_2",
        "Module_2_Cell_Temperature_0",
        "Module_2_Cell_Temperature_1",
        "Module_2_Cell_Temperature_2",
        "Module_3_Cell_Temperature_0",
        "Module_3_Cell_Temperature_1",
        "Module_3_Cell_Temperature_2",
        "Module_4_Cell_Temperature_0",
        "Module_4_Cell_Temperature_1",
        "Module_4_Cell_Temperature_2",
        "Module_5_Cell_Temperature_0",
        "Module_5_Cell_Temperature_1",
        "Module_5_Cell_Temperature_2",
        "BMS_Voltage_Module_ID",
        "Module_0_Cell_Voltage_0",
        "Module_0_Cell_Voltage_1",
        "Module_0_Cell_Voltage_2",
        "Module_0_Cell_Voltage_3",
        "Module_0_Cell_Voltage_4",
        "Module_1_Cell_Voltage_0",
        "Module_1_Cell_Voltage_1",
        "Module_1_Cell_Voltage_2",
        "Module_1_Cell_Voltage_3",
        "Module_1_Cell_Voltage_4",
        "Module_2_Cell_Voltage_0",
        "Module_2_Cell_Voltage_1",
        "Module_2_Cell_Voltage_2",
        "Module_2_Cell_Voltage_3",
        "Module_2_Cell_Voltage_4",
        "Module_3_Cell_Voltage_0",
        "Module_3_Cell_Voltage_1",
        "Module_3_Cell_Voltage_2",
        "Module_3_Cell_Voltage_3",
        "Module_3_Cell_Voltage_4",
        "Module_4_Cell_Voltage_0",
        "Module_4_Cell_Voltage_1",
        "Module_4_Cell_Voltage_2",
        "Module_4_Cell_Voltage_3",
        "Module_4_Cell_Voltage_4",
        "Module_5_Cell_Voltage_0",
        "Module_5_Cell_Voltage_1",
        "Module_5_Cell_Voltage_2",
        "Module_5_Cell_Voltage_3",
        "Module_5_Cell_Voltage_4",
        "BMS_Cell_SOC_Module_ID",
        "Module_0_Cell_SOC_0",
        "Module_0_Cell_SOC_1",
        "Module_0_Cell_SOC_2",
        "Module_0_Cell_SOC_3",
        "Module_0_Cell_SOC_4",
        "Module_1_Cell_SOC_0",
        "Module_1_Cell_SOC_1",
        "Module_1_Cell_SOC_2",
        "Module_1_Cell_SOC_3",
        "Module_1_Cell_SOC_4",
        "Module_2_Cell_SOC_0",
        "Module_2_Cell_SOC_1",
        "Module_2_Cell_SOC_2",
        "Module_2_Cell_SOC_3",
        "Module_2_Cell_SOC_4",
        "Module_3_Cell_SOC_0",
        "Module_3_Cell_SOC_1",
        "Module_3_Cell_SOC_2",
        "Module_3_Cell_SOC_3",
        "Module_3_Cell_SOC_4",
        "Module_4_Cell_SOC_0",
        "Module_4_Cell_SOC_1",
        "Module_4_Cell_SOC_2",
        "Module_4_Cell_SOC_3",
        "Module_4_Cell_SOC_4",
        "Module_5_Cell_SOC_0",
        "Module_5_Cell_SOC_1",
        "Module_5_Cell_SOC_2",
        "Module_5_Cell_SOC_3",
        "Module_5_Cell_SOC_4",
        "BMS_Heartbeat",
        "Valid CRC",
        "Timestamp"
    ]

    all_str = ""; question_marks = ""
    for idx, data in enumerate(datas):
        all_str += data
        question_marks += "?"
        if (idx < len(datas) - 1):
            all_str += ", "
            question_marks += ", "

    return (all_str, question_marks)