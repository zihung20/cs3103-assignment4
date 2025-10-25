import asyncio
from aioquic.asyncio.client import connect
from aioquic.quic.configuration import QuicConfiguration
from aioquic.asyncio import QuicConnectionProtocol
from config import HOST, PORT

class GameClient:
    def __init__(self, conn:QuicConnectionProtocol):
        self.conn = conn
        self.quic = conn._quic
        self.reliable_sid = self.quic.get_next_available_stream_id()

    def send_reliable(self, data: bytes, end=False):
        self.quic.send_stream_data(self.reliable_sid, data, end_stream=end)
        self.conn.transmit()

    def send_unreliable(self, data: bytes):
        self.quic.send_datagram_frame(data)
        self.conn.transmit()

async def receive_user_input()->str:
    loop = asyncio.get_running_loop()
    while True:
        msg = await loop.run_in_executor(None, input, "You: ")
        if msg.lower() in {"quit", "exit"}:
            return ""
        
        return msg

async def main():
    cfg = QuicConfiguration(is_client=True, alpn_protocols=["echo"])
    cfg.verify_mode = False
    cfg.max_datagram_frame_size = 65536

    async with connect(HOST, PORT, configuration=cfg) as conn:
        await conn.wait_connected()
        gc = GameClient(conn)

        while True:
            user_input = await receive_user_input()
            if not user_input:
                break
            elif user_input.startswith("R"):
                gc.send_reliable(user_input.encode())
            else:
                gc.send_unreliable(user_input.encode())

        await asyncio.sleep(0.5)

asyncio.run(main())
