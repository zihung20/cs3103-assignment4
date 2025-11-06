import socket, time, asyncio, os
from gameNetApiSender import GameSender
from data import mock_client_msgs
from config import HOST, PORT, MESSAGE_ENCODING
import random

def main():
    gs = GameSender(HOST, PORT)
    # tests = ['./test/longtext.txt', './test/chinese.txt', './test/shorttext.txt', './test/longtext.txt']

    
    data = []
    with open("./test/output.txt", "r", encoding=MESSAGE_ENCODING) as f:
        long_text = f.read().splitlines()
        data.extend(long_text[i].encode(MESSAGE_ENCODING) for i in range(len(long_text)))
    # for i in range(random.randint(1, len(mock_client_msgs))):
    #     msg = mock_client_msgs[random.randint(0, len(mock_client_msgs) - 1)]
    #     payload_bytes = str(msg).encode('utf-8')
    #     data.append(payload_bytes)

    # print("Sending reliable packets now...")
    # gs.send_data(data, True)
    # # await asyncio.sleep(0.01)
    # time.sleep(8)

    is_reliable = True
    if is_reliable:
        print("Sending reliable packets now...")
    else:
        print("Sending unreliable packets now...")
        
    gs.send_data(data, is_reliable)

# asyncio.run(main())
main()