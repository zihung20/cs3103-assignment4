import asyncio, struct, time, random
from aioquic.asyncio.client import connect
from aioquic.quic.configuration import QuicConfiguration
from aioquic.asyncio import QuicConnectionProtocol
from config import HOST, PORT, HEADER_FORMAT

class GameClient:
    def __init__(self, conn:QuicConnectionProtocol):
        self.conn = conn
        self.quic = conn._quic
        self.reliable_sid = self.quic.get_next_available_stream_id()

    def generate_packet(self, sequence_number:int, data: bytes):
        time_now = int(time.time() * 1000) & 0xFFFFFFFF
        payload_len = len(data)
        header = struct.pack(HEADER_FORMAT, sequence_number, payload_len, time_now)
        return header + data

    def send_data(self, data:bytes | str, is_reliable=False):
        data_bytes = bytes(data)
        if is_reliable:
            self.send_reliable(data_bytes)
        else:
            self.send_unreliable(data_bytes)
            
    def send_reliable(self, data: bytes, end=False):
        d = self.generate_packet(69, data)
        self.quic.send_stream_data(self.reliable_sid, d, end_stream=end)
        self.conn.transmit()

    def send_unreliable(self, data: bytes):
        d = self.generate_packet(69, data)
        self.quic.send_datagram_frame(d)
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
            gc.send_data(user_input.encode(), random.choice([True, False]))

        await asyncio.sleep(0.5)

asyncio.run(main())
