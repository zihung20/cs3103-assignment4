from socket import *
from utils import parse_packet, check_sender_packet, generate_ack, get_time_passed
from config import SENDER_SEQ, SENDER_CHANNEL, SENDER_FLAGS, SENDER_TIMESTAMP
import time

class GameReceiver():
    def __init__(self, host: str, server_port:int):
        self.host = host
        self.server_port = server_port
        self.expect_sequence = 0
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverSocket.bind((host, self.server_port))
        # metrics
        self.jitter_ms = 0.0
        self.prev_time_passed_ms = 0.0
        self.total_bytes = 0
        self.total_time_ms = 0.0
        print(f"Server is listening on port {self.server_port}...")
    
    def check(self, metadata:tuple, payload: bytes):
        if not check_sender_packet(metadata, payload):
            print(f"corrupt packet {metadata}, discard")
            return False
        else:
            sequence = metadata[SENDER_SEQ]
            if sequence != self.expect_sequence:
                print(f"out of order packet {metadata}, expect {self.expect_sequence}, discard")
                return False
            self.expect_sequence += 1
            return True
        
    def send_ack(self, clientAddress:tuple, ack_sequence:int, to_stop:bool=False) -> None:
        ack_packet = generate_ack(ack_sequence, to_stop)
        self.serverSocket.sendto(ack_packet, clientAddress)

    def receive_data(self, timeout_ms:int=1000, idle_ms:int=10000) -> bytes|None:
        buffer = {}
        count = 0 # counter for attempts
        max_attempts = 2

        last_activity = time.time()

        last_seq_seen = False
        last_seq_index = None
        is_last = False
        is_reliable = True
        while True:
            per_pkt_deadline = time.time() + (timeout_ms / 1000.0)
            got_something = False
            clientAddress = None

            while time.time() < per_pkt_deadline:
                time_remaining = per_pkt_deadline - time.time()

                self.serverSocket.settimeout(max(0.0, min(time_remaining, idle_ms / 1000)))

                try:
                    packet, clientAddress = self.serverSocket.recvfrom(2048)
                except timeout:
                    continue # wait for the packet

                got_something = True
                last_activity = time.time()

                metadata, payload = parse_packet(packet)

                if metadata[SENDER_CHANNEL] == 0:
                    is_reliable = False

                if not self.check(metadata, payload) and is_reliable:
                    self.send_ack(clientAddress, self.expect_sequence)
                else:
                    if not is_reliable:
                        max_attempts = 1 # for unreliable channel
                    if metadata[SENDER_SEQ] not in buffer:
                        print(f"Received something {metadata}")
                        buffer[metadata[SENDER_SEQ]] = (metadata, payload)

                    if self.is_last_packet(metadata):
                        print("Received last packet, send back ack")
                        last_seq_seen = True
                        last_seq_index = metadata[SENDER_SEQ]
                        is_last = True
                        # self.send_ack(clientAddress, self.expect_sequence, True)
                        ##maybe cannot immediately break, need to wait for a bit to see if any more packets arrive

                    self.print_stats(metadata, payload)
                    if not is_last and is_reliable:
                        # prevent send the last packet ack twice
                        self.send_ack(clientAddress, self.expect_sequence)

                    count = 0
                    break

            if not got_something:
                count += 1
                
                if count >= max_attempts:
                    print(f"Failed after one retransmission for  seq {self.expect_sequence}, skipping it.")
                    self.expect_sequence += 1
                    count = 0
                else:
                    if clientAddress and not is_reliable:
                        self.send_ack(clientAddress, self.expect_sequence)

            if last_seq_seen and last_seq_index is not None and self.expect_sequence > last_seq_index:
                break

            # timeout for receive nothing
            if (time.time() - last_activity) * 1000 > idle_ms:
                print("Idle timeout reached")
                break

        # After timeout or received last packet, reconstruct whatever packets we have
        if buffer:
            print("reconstruct packet of what we have")
            data = self.reconstruct_packets(buffer)
            if clientAddress and is_reliable:
                self.send_ack(clientAddress, self.expect_sequence, True)

            return data
        
        return None

    def reconstruct_packets(self, buffer:dict) -> bytes:
        data = b""
        for seq in sorted(buffer.keys()):
            _, payload = buffer[seq]
            data += payload
        return data

    def is_last_packet(self, metadata:tuple) -> bool:
        """
        return true if we received the last packet, and the previous other packets has been received too
        """
        return metadata[SENDER_FLAGS] == 1 and metadata[SENDER_SEQ] == self.expect_sequence - 1
    
    def print_stats(self, metadata:tuple, payload:bytes) -> None:
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
