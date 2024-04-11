from serial import Serial
from cobs import cobs
from messages_pb2 import IMUData
from google.protobuf.json_format import MessageToDict
import json
from time import time

PORT = "/dev/cu.usbmodem101"

ser = Serial(PORT, 115200)
buffer = b''
in_message = False

start_time = 0.
stop_time = 0.

N = 10000
n_rec = 0

last_time = 0.

while True:
    data = ser.read(1)
    # n_rec += 1
    # print(f"N: {n_rec}, data: {data}")
    if data == bytes([0x00]):
        if in_message and len(buffer) > 0:
            # Stop flag detected, process the message
            try:
                # COBS decode
                message = cobs.decode(buffer)
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

 