from contextlib import asynccontextmanager
from aioquic.asyncio.client import connect
from aioquic.quic.configuration import QuicConfiguration
from aioquic.asyncio.protocol import QuicConnectionProtocol
import utils

class GameSender:
    def __init__(self, conn:QuicConnectionProtocol, cm=None):
        self.conn = conn
        self.quic = conn._quic
        self.reliable_sid = self.quic.get_next_available_stream_id()
        self._cm = cm

    def send_data(self, seq_no, data, is_reliable=False):
        data_bytes = bytes(data)
        if is_reliable:
            self.send_reliable(seq_no, data_bytes)
        else:
            self.send_unreliable(seq_no, data_bytes)

    def send_reliable(self, seq_no, data, end=False):
        d = utils.generate_packet(seq_no, data)
        self.quic.send_stream_data(self.reliable_sid, d, end_stream=end)
        self.conn.transmit()

    def send_unreliable(self, seq_no, data):
        df = utils.generate_packet(seq_no, data)
        self.quic.send_datagram_frame(df)
        self.conn.transmit()


# create the quic sender as an async context manager
@asynccontextmanager
async def create_sender(host, port):
    cfg = QuicConfiguration(
        is_client=True,
        alpn_protocols=["game"],
        verify_mode=False,
        max_datagram_frame_size=65536
    )

    cm = connect(host, port, configuration=cfg)
    conn = await cm.__aenter__()
    await conn.wait_connected()

    sender = GameSender(conn, cm)

    try:
        yield sender
    finally:
        # ensure clean shutdown
        await cm.__aexit__(None, None, None)