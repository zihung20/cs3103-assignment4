from aioquic.asyncio.client import connect
from aioquic.quic.configuration import QuicConfiguration
from aioquic.asyncio.protocol import QuicConnectionProtocol
import utils

class GameSender:
    def __init__(self, conn:QuicConnectionProtocol):
        self.conn = conn
        self.quic = conn._quic
        self.reliable_sid = self.quic.get_next_available_stream_id()
        self._cm = None  # placeholder for async context manager

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

    async def close(self):
        """Close the QUIC connection (exit the connect() context)."""
        if self._cm is not None:
            try:
                await self._cm.__aexit__(None, None, None)
            finally:
                self._cm = None

    # static function to create an instance asynchronously
    @classmethod
    async def create(cls, host, port):
        cfg = QuicConfiguration(
            is_client=True,
            alpn_protocols=["game"],
            verify_mode=False,
            max_datagram_frame_size=65536
        )
        cm = connect(host, port, configuration=cfg)   # async context manager
        conn = await cm.__aenter__()                  # enter and get protocol
        await conn.wait_connected()
        obj = cls(conn)
        obj._cm = cm                                   # keep cm so close() can exit it
        return obj
