from gameNetApiReceiver import GameReceiver
import asyncio
from config import PORT, TIME_LIMIT_MS

async def main():
    print("Starting Game Receiver...")
    temp = GameReceiver('0.0.0.0', PORT)
    while True:
        data = temp.receive_data(TIME_LIMIT_MS)
        if not data:
            print("No more data received, exiting.")
            break
        print(f"Data received using the api: {data.decode()}")

    
asyncio.run(main())