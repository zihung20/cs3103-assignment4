import random, time, asyncio
from gameNetApiSender import GameSender
from config import HOST, PORT
from data import mock_client_msgs

async def main():
    gs = await GameSender.create(HOST, PORT)

    random.seed(time.time())   
    seq_start = random.randint(0, 2048)

    for i in range(100):
        data = str(mock_client_msgs[random.randint(0, len(mock_client_msgs)-1)])
        gs.send_data(seq_start + i, data.encode(), random.choice([True, False]))

    await asyncio.sleep(0.5)

    await gs.close()

asyncio.run(main())