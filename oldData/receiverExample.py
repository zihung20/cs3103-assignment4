from gameNetApiReceiver import GameReceiver
import asyncio
from config import HOST, PORT

async def main():
    print("Starting Game Receiver...")
    await GameReceiver.create(HOST, PORT)
    

asyncio.run(main())