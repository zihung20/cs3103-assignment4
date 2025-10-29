import asyncio
from aioquic.asyncio import server
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived, DatagramFrameReceived
from config import TIME_LIMIT_MS, METADATA_TIMESTAMP_MS, METADATA_SEQ_NO
import utils

class GameReceiver(QuicConnectionProtocol):
    def __init__(self, *args, process_fn=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.jitter_ms = 0.0
        self.prev_time_passed_ms = 0.0
        self.total_bytes = 0
        self.total_time_ms = 0.0
        self.process_fn = process_fn
        
    def quic_event_received(self, event):
        if isinstance(event, (StreamDataReceived, DatagramFrameReceived)):
            self.process_payload(event)
    
    def process_payload(self, event: StreamDataReceived | DatagramFrameReceived):
        metadata, payload = utils.parse_packet(event.data)
        time_passed = utils.get_time_passed(metadata[METADATA_TIMESTAMP_MS])
        
        if time_passed > TIME_LIMIT_MS:
            print(f"[WARNING] Packet {metadata[METADATA_SEQ_NO]} exceeded time limit of {TIME_LIMIT_MS} ms (actual: {time_passed} ms)")
            return 
        
        throughput = self.calc_throughput(len(payload), time_passed)
        jitter = self.calc_jitter(time_passed)

        if isinstance(event, StreamDataReceived):
            title = f"stream {event.stream_id}"
        else:
            title = "datagram"
        
        print(f"[{title}] {metadata}")
        print(f"    Latency: {time_passed} ms")
        print(f"    Throughput: {throughput:.2f} bytes/s")
        print(f"    Jitter: {jitter:.2f} ms\n")

        if self.process_fn:
            self.process_fn(metadata, payload)

    def calc_throughput(self, payload_size, time_passed_ms):
        self.total_bytes += payload_size
        self.total_time_ms += time_passed_ms

        return self.total_bytes / max(self.total_time_ms * 1000, 1e-6)  # in bytes per seconds
    
    def calc_jitter(self, time_passed_ms):
        # Using RFC 3550 formula, J = J + (|D(i-1,i)| - J)/16, where D is the difference in time passed between packets
        diff = abs(time_passed_ms - self.prev_time_passed_ms)
        self.jitter_ms += (diff - self.jitter_ms) / 16
        self.prev_time_passed_ms = time_passed_ms

        return self.jitter_ms
    
    @classmethod
    async def create(cls, host, port, process_fn=None):
        cfg = QuicConfiguration(is_client=False, alpn_protocols=["game"], max_datagram_frame_size=65536)
        cfg.load_cert_chain("cert.pem", "key.pem")
        await server.serve(
            host, 
            port, 
            configuration=cfg, 
            create_protocol=lambda *args, **kwargs: cls(*args, process_fn=process_fn, **kwargs)
        )
        await asyncio.get_running_loop().create_future()
