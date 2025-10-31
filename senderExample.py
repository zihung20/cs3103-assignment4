import socket, time, asyncio, os
from gameNetApiSender import GameSender
from data import mock_client_msgs
from config import PORT

HOST = socket.gethostbyname("receiver")

async def main():
    temp = GameSender(HOST, PORT)
    with open("longtext.txt", "r") as f:
        text = f.read()
        for i in range(1):
            temp.send_data(text.encode(), True)
            await asyncio.sleep(0.01)

asyncio.run(main())