from socket import socket, AF_INET, SOCK_DGRAM, timeout
from utils import parse_packet, check_sender_packet, generate_ack, get_time_passed, ms_to_seconds, generate_stats
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

        # Data collection
        self.actual_packet_count = 0
        self.jitters = []
        self.throughputs = []
        self.latency = []
        self.total_packet = 0
        self.time_stamp = []
        self.latest_seq = 0

    def check(self, metadata: tuple, payload: bytes):
        if not check_sender_packet(metadata, payload):
            print(f"corrupt packet {metadata}, discard")
            return False
        
        return True

    def send_ack(self, sender_address: tuple, ack_sequence: int, sender_timestamp:int, to_stop: bool = False) -> None:
        ack_packet = generate_ack(ack_sequence, to_stop, sender_timestamp)
        self.receiver_socket.sendto(ack_packet, sender_address)

    def receive_data(self, callback_fn, timeout_ms: int = 1000, idle_ms: int = 10000) -> list[bytes] | None:
        receive_buffer = GameNetBuffer(callback_fn)

        last_activity = time.time()
        is_reliable = False
        deadline_current_seq = time.time() + idle_ms / 1000
        count = 1

        while time.time() - last_activity < ms_to_seconds(idle_ms):
            remaining_time = deadline_current_seq - time.time()
            print(f"Waiting for packet {receive_buffer.get_next_expected_sequence()} remaining time: {remaining_time:.2f} s")
            timeout_setting = max(0.01, min(ms_to_seconds(timeout_ms), remaining_time))
            self.receiver_socket.settimeout(timeout_setting)
            
            try:
                packet, addr = self.receiver_socket.recvfrom(2048)
                metadata, payload = parse_packet(packet)
                self.packets_count += 1

                print(f"Received packet from {addr}: {metadata}")

                if metadata[SENDER_CHANNEL] == 1:
                    is_reliable = True
                
                if self.check(metadata, payload):
                    if not is_reliable:
                        callback_fn(payload)
                        self.print_stats(metadata, payload)
                        self.latest_seq = max(self.latest_seq, metadata[SENDER_SEQ])
                        deadline_current_seq = time.time() + timeout_ms / 1000
                        receive_buffer.add_packet(metadata[SENDER_SEQ], payload)
                    else:
                        if metadata[SENDER_SEQ] == receive_buffer.get_next_expected_sequence():
                            deadline_current_seq = time.time() + timeout_ms / 1000
                            self.actual_packet_count += 1
                            self.print_stats(metadata, payload)
                            deadline_current_seq = time.time() + timeout_ms / 1000
                            count = 1
                        receive_buffer.add_packet(metadata[SENDER_SEQ], payload)
                        next_expect_seq = receive_buffer.get_next_expected_sequence()
                        self.send_ack(addr, next_expect_seq, metadata[SENDER_TIMESTAMP])
                                                
                if is_reliable and self.is_last_packet(metadata, receive_buffer):
                    print("Last packet received, stop receiving.")
                    self.total_packet = metadata[SENDER_SEQ] + 1 # data collection
                    break

                last_activity = time.time()
            except timeout:
                if time.time() >= deadline_current_seq:
                    print(f"Exceeded time, skip the packet.")
                    receive_buffer.skip_current_offset()
                    deadline_current_seq = time.time() + timeout_ms / 1000 * count
                    count += 1


        print("Total packets received:", self.packets_count)
        data_received = receive_buffer.get_ordered_packets()
        
        # data collection
        if self.packets_count != 0 and is_reliable:
            generate_stats(jitters=self.jitters, 
                        throughputs=self.throughputs, 
                        latency=self.latency, 
                        packet_received=self.actual_packet_count, 
                        total_packet=receive_buffer.get_next_expected_sequence(),
                        time_stamps=self.time_stamp)
            
        if self.packets_count != 0 and not is_reliable:
            generate_stats(jitters=self.jitters, 
                        throughputs=self.throughputs, 
                        latency=self.latency, 
                        packet_received=self.packets_count, 
                        total_packet=self.latest_seq + 1,
                        time_stamps=self.time_stamp)
    
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

        self.jitters.append(jitter)
        self.throughputs.append(throughput)
        self.latency.append(time_passed_ms)
        self.time_stamp.append(metadata[SENDER_TIMESTAMP])
        
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
    
    def is_last_packet(self, metadata:tuple, receive_buffer:GameNetBuffer) -> bool:
        """
        return true if we received the last packet, and the previous other packets has been received too
        """
        return metadata[SENDER_FLAGS] == 1 and metadata[SENDER_SEQ] == receive_buffer.get_next_expected_sequence() - 1