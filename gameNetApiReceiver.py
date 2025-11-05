from socket import socket, AF_INET, SOCK_DGRAM, timeout
from utils import parse_packet, check_sender_packet, generate_ack, get_time_passed, ms_to_seconds
from config import SENDER_SEQ, SENDER_CHANNEL, SENDER_FLAGS, SENDER_TIMESTAMP
import time
from gameNetBuffer import GameNetBuffer

class GameReceiver():
    def __init__(self, receiver_host: str, receiver_port:int):
        self.receiver_host = receiver_host
        self.receiver_port = receiver_port
        
        self.receiver_socket = socket(AF_INET, SOCK_DGRAM)
        self.receiver_socket.bind((self.receiver_host, self.receiver_port))
        
        self.packets_count = 0

        # metrics
        self.jitter_ms = 0.0
        self.prev_time_passed_ms = 0.0
        self.total_bytes = 0
        self.total_time_ms = 0.0
        print(f"Server is listening on port {self.receiver_port}...")

    def check(self, metadata: tuple, payload: bytes):
        if not check_sender_packet(metadata, payload):
            print(f"corrupt packet {metadata}, discard")
            return False
        
        return True

    def send_ack(self, sender_address: tuple, ack_sequence: int, to_stop: bool = False) -> None:
        ack_packet = generate_ack(ack_sequence, to_stop)
        self.receiver_socket.sendto(ack_packet, sender_address)

    def receive_data(self, callback_fn, timeout_ms: int = 1000, idle_ms: int = 10000) -> list[bytes] | None:
        receive_buffer = GameNetBuffer()
        count = 0
        max_attempts = 5 # initial max attempts, more times allow to receive first packet

        last_activity = time.time()
        is_reliable = False
        
        # set idle timeout
        # if exceed idle timeout without receiving any packets, stop receiving
        while time.time() - last_activity < ms_to_seconds(idle_ms):
            if count < max_attempts:
                self.receiver_socket.settimeout(ms_to_seconds(timeout_ms))
                
                try:
                    packet, addr = self.receiver_socket.recvfrom(2048)
                    metadata, payload = parse_packet(packet)
                    self.packets_count += 1

                    print(f"Received packet from {addr}: {metadata}")
                    self.print_stats(metadata, payload)

                    if not is_reliable and metadata[SENDER_CHANNEL] == 1:
                        max_attempts = 2
                        is_reliable = True

                    if max_attempts == 2 and not is_reliable:
                        max_attempts = 1  # for unreliable channel
                    
                    if self.check(metadata, payload):
                        next_expect_seq = receive_buffer.get_next_expected_sequence()

                        if not is_reliable or metadata[SENDER_SEQ] == next_expect_seq:
                            callback_fn(payload)
                        
                        receive_buffer.add_packet(metadata[SENDER_SEQ], payload)
                    
                    if is_reliable:
                        next_expect_seq = receive_buffer.get_next_expected_sequence()
                        self.send_ack(addr, next_expect_seq)

                    count = 0
                    last_activity = time.time()
                except timeout:
                    count += 1
            else:
                print(f"Exceeded maximum attempts ({max_attempts}), skip the packet.")
                receive_buffer.skip_current_offset()
                count = 0

            if time.time() - last_activity >= ms_to_seconds(idle_ms):
                print("Idle timeout reached during receiving")
                break

        print("Total packets received:", self.packets_count)
        data_received = receive_buffer.get_ordered_packets()
        
        self.packets_count = 0

        return data_received

    def print_stats(self, metadata: tuple, payload: bytes) -> None:
        channel_title = "Reliable" if metadata[SENDER_CHANNEL] == 1 else "Unreliable"
        time_passed_ms = get_time_passed(metadata[SENDER_TIMESTAMP])
        payload_size = len(payload)
        throughput = self.calc_throughput(payload_size, time_passed_ms)
        jitter = self.calc_jitter(time_passed_ms)
        
        print(f"[{channel_title}]\t{metadata}")
        print(f"\tLatency: {time_passed_ms} ms")
        print(f"\tThroughput: {throughput:.2f} bytes/s")
        print(f"\tJitter: {jitter:.2f} ms\n")
    
    def calc_throughput(self, payload_size:int, time_passed_ms:int):
        self.total_bytes += payload_size
        self.total_time_ms += time_passed_ms

        return self.total_bytes / max(self.total_time_ms / 1000, 1e-6)  # in bytes per seconds
    
    def calc_jitter(self, time_passed_ms:int):
        # Using RFC 3550 formula, J = J + (|D(i-1,i)| - J)/16, where D is the difference in time passed between packets
        diff = abs(time_passed_ms - self.prev_time_passed_ms)
        self.jitter_ms += (diff - self.jitter_ms) / 16
        self.prev_time_passed_ms = time_passed_ms

        return self.jitter_ms
