from serial import Serial
from cobs import cobs
import msg.messages_pb2 as messages_pb2
from google.protobuf.json_format import MessageToDict
import json
from time import time
from enum import Enum

PORT = "/dev/cu.usbmodem212101"

ser = Serial(PORT, 115200)
buffer = b''
in_message = False

start_time = 0.
stop_time = 0.

N = 10000
n_rec = 0

last_time = 0.

class PacketID(Enum):
    IMU_DATA = 1
    STATUS = 2
    DEVICE_INFO = 3
    COMMAND = 4

def decode_packet(packet: bytes):
    packet_id = PacketID(packet[0])
    print(f"Packet ID: {packet_id}")
    decoded = cobs.decode(packet[1:])
    if packet_id == PacketID.IMU_DATA:
        msg = messages_pb2.IMUData.FromString(decoded)
        print(f"cnt:{msg.count:,}, a_x:{msg.acc_x:+.2f},"
                f"a_y:{msg.acc_y:+.2f}, a_z:{msg.acc_z:+.2f}")
    elif packet_id == PacketID.STATUS:
        msg = messages_pb2.Status.FromString(decoded)
    elif packet_id == PacketID.DEVICE_INFO:
        msg = messages_pb2.DeviceInfo.FromString(decoded)
    return msg

while True:
    """
    data = ser.read(1)
    # n_rec += 1
    # print(f"N: {n_rec}, data: {data}")
    if data == bytes([0x00]):
        if in_message and len(buffer) > 0:
            # Stop flag detected, process the message
            try:
                # COBS decode
                message = cobs.decode(buffer[1:])
                # protobuf decode
                message = IMUData.FromString(message)
                # d = MessageToDict(message, including_default_value_fields=True)
                # print(json.dumps(d, indent=2))
                
                print(f"cnt:{message.count}, a_x:{message.acc_x:+.2f}, a_y:{message.acc_y:+.2f}, a_z:{message.acc_z:+.2f}")
                
                # N = 10_000
                # if message.count % N == 0:
                #     print(f"cnt:{message.count:,}, a_x:{message.acc_x:+.2f},"
                #         f"a_y:{message.acc_y:+.2f}, a_z:{message.acc_z:+.2f},"
                #         f"freq: {N / (time() - last_time):.2f} Hz")
                #     last_time = time()
                
                # if message.count == 0:
                #     start_time = time()
                # elif message.count == N - 1:
                #     stop_time = time()
                #     print(f"Time elapsed: {stop_time - start_time:.3f}, frequency: {N / (stop_time - start_time):.1f} Hz")
                # n_rec += 1
                # print(f"Received {n_rec} messages")
                # print(f"msg count: {message.count}")
            except Exception as e:
                print(f"An error occurred: {e}") 
            finally:
                buffer = b''
                in_message = False
        else:
            # Start flag detected, start collecting the message
            in_message = True
    elif in_message:
        buffer += data
    """   

    data = ser.read(1)
    if len(data) > 0:
        if data == bytes([0x00]):
            if in_message:
                if len(buffer) > 0:
                    # stop flag, end of packet
                    message = decode_packet(buffer)
                    print(f"cn2t:{message.count}, a_x:{message.acc_x:+.2f}, a_y:{message.acc_y:+.2f}, a_z:{message.acc_z:+.2f}")
                    buffer = b''
                    in_message = False
                else:
                    # empty packet, treat as new start flag
                    pass
            else:
                # start flag
                in_message = True
        elif in_message:
            buffer += data

 