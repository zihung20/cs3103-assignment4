import asyncio, struct, time, argparse
from aioquic.asyncio import serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived, DatagramFrameReceived
from config import HOST, PORT, HEADER_FORMAT, TIME_LIMIT_MS

class GameServer(QuicConnectionProtocol):

    def get_time_passed(self, timestamp: int):
        time_now = int(time.time() * 1000) & 0xFFFFFFFF
        return time_now - timestamp
    
    def parse_packet(self, packet: bytes):
        header_size = struct.calcsize(HEADER_FORMAT)
        seq_no, payload_len, timestamp_ms = struct.unpack(HEADER_FORMAT, packet[:header_size])
        payload = packet[header_size:]
        metadata = (seq_no, payload_len, timestamp_ms)
        return metadata, payload

    def quic_event_received(self, event):
        if isinstance(event, StreamDataReceived) or isinstance(event, DatagramFrameReceived):
            self.process_payload(event)
    
    def process_payload(self, event: StreamDataReceived | DatagramFrameReceived):
        metadata, payload = self.parse_packet(event.data)
        time_passed = self.get_time_passed(metadata[2])
        if time_passed > TIME_LIMIT_MS:
            #drop it
            pass
        else:
            if isinstance(event, StreamDataReceived):
                title = f"stream{event.stream_id}"
            else:
                title = "datagram"            
            print(f"[{title}] {metadata} {payload.decode()}")

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="server")
    ap.add_argument("--port", type=int, default="4433")
    return ap.parse_args()

async def main():
    cfg = QuicConfiguration(is_client=False, alpn_protocols=["echo"], max_datagram_frame_size=65536)
    cfg.load_cert_chain("cert.pem", "key.pem")
    args = parse_args()
    await serve(args.host, args.port, configuration=cfg, create_protocol=GameServer)
    await asyncio.get_running_loop().create_future()

asyncio.run(main())
