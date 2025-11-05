from gameNetApiReceiver import GameReceiver
import asyncio
from config import HOST, PORT, TIME_LIMIT_MS, MESSAGE_ENCODING

def main():
    print("Starting Game Receiver...")

    gr = GameReceiver(HOST, PORT)
    buffer = []
    
    while True:
        data = gr.receive_data(TIME_LIMIT_MS)
        
        if not data:
            print("No more data received, exiting.")
            break

        for d in data:
            print(f"Data received using the api: {d.decode(MESSAGE_ENCODING)}")
            buffer.append(d.decode(MESSAGE_ENCODING))

    # with open("received_messages.txt", "w", encoding=MESSAGE_ENCODING) as f:
    #     for line in buffer:
    #         f.write(line + "\n")

# asyncio.run(main())
main()