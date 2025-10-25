import asyncio
from aioquic.asyncio import serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived, DatagramFrameReceived
from config import HOST, PORT

class GameServer(QuicConnectionProtocol):
    def quic_event_received(self, event):
        if isinstance(event, StreamDataReceived):
            print(f"[stream {event.stream_id}] {event.data.decode()}")
            
        elif isinstance(event, DatagramFrameReceived):
            print(f"[datagram] {event.data.decode()}")

async def main():

    cfg = QuicConfiguration(is_client=False, alpn_protocols=["echo"], max_datagram_frame_size=65536)
    cfg.load_cert_chain("cert.pem", "key.pem")
    await serve(HOST, PORT, configuration=cfg, create_protocol=GameServer)
    await asyncio.get_running_loop().create_future()

asyncio.run(main())
