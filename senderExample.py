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

    is_reliable = True
    if is_reliable:
        print("Sending reliable packets now...")
    else:
        print("Sending unreliable packets now...")
        
    gs.send_data(data, is_reliable)

# asyncio.run(main())
main()