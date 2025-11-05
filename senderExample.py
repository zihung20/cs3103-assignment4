import socket, time, asyncio, os
from gameNetApiSender import GameSender
from data import mock_client_msgs
from config import HOST, PORT, MESSAGE_ENCODING
import random

def main():
    gs = GameSender(HOST, PORT)
    # tests = ['./test/longtext.txt', './test/chinese.txt', './test/shorttext.txt', './test/longtext.txt']

    data = [
        "hello",
        "this is a test message",
        "sending reliable packets using gameNetApiSender",
        "packet loss simulation",
        "final message",
        "testing 1 2 3",
        "another message to send",
    ]
    data = [d.encode(MESSAGE_ENCODING) for d in data]

    # for i in range(random.randint(1, len(mock_client_msgs))):
    #     msg = mock_client_msgs[random.randint(0, len(mock_client_msgs) - 1)]
    #     payload_bytes = str(msg).encode('utf-8')
    #     data.append(payload_bytes)

    # print("Sending reliable packets now...")
    # gs.send_data(data, True)
    # # await asyncio.sleep(0.01)
    # time.sleep(8)

    print("Sending unreliable packets now...")
    gs.send_data(data, False)

# asyncio.run(main())
main()