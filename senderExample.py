import socket, time, asyncio, os
from gameNetApiSender import GameSender
from data import mock_client_msgs
from config import PORT

HOST = socket.gethostbyname("receiver")

async def main():
    temp = GameSender(HOST, PORT)
    tests = ['./test/longtext.txt', './test/chinese.txt', './test/shorttext.txt', './test/longtext.txt']

    for testfile in tests:
        if not os.path.exists(testfile):
            print(f"Test file {testfile} does not exist, skipping.")
            continue
        with open(testfile, "r", encoding="utf-8") as f:
            text = f.read()
            print(f"Sending data from {testfile}...")
            temp.send_data(text.encode(), True)
            await asyncio.sleep(0.01)

asyncio.run(main())