from socket import socket, AF_INET, SOCK_DGRAM, gethostbyname
from utils import parse_ack, check_ack_corrupt, build_sender_packet, generate_seq_no, get_offset_from_seq
from config import TIME_LIMIT_MS, WINDOW_SIZE, SENDER_RETRY_LIMIT, ACK_SEQUENCE, ACK_FLAGS
import select, time
import random

class GameSender:
    def __init__(self, receiver_host: str, receiver_port: int):
        self.receiver_host = receiver_host
        self.receiver_ip = gethostbyname(receiver_host)
        self.receiver_port = receiver_port
        self.receiver_address = (self.receiver_ip, receiver_port)
        self.receiver_socket = socket(AF_INET, SOCK_DGRAM)

        print(f"Send to {self.receiver_address}")

    def send_data(self, data: list[bytes], is_reliable: bool) -> None:        
        if is_reliable:
            self.send_reliable_packets(data)
        else:
            self.send_unreliable_packets(data)

    def send_unreliable_packets(self, data: list[bytes]) -> None:
        for i, chunk in enumerate(data):
            packet = build_sender_packet(0, i, chunk, False, True)
            self.receiver_socket.sendto(packet, self.receiver_address)
            time.sleep(0.001)

    def send_reliable_packets(self, data: list[bytes]) -> None:
        random.seed(time.time())
        start_seq = random.randint(1, 0xFFFF)  # random initial sequence number
        left = 0
        right = 0
        sender_timeout_ms = TIME_LIMIT_MS / 20 # random guess

        time_start = None

        def start_timer():
            nonlocal time_start
            if time_start is None: 
                time_start = time.time()

        def time_left():
            if time_start is None:
                return sender_timeout_ms / 1000
            elapsed = time.time() - time_start
            return max(0.0, sender_timeout_ms / 1000 - elapsed)
        
        def stop_timer():
            nonlocal time_start
            time_start = None

        def retick_timer():
            nonlocal time_start
            time_start = time.time()

        count = 0

        while left < len(data):
            # send WINDOW_SIZE packets
            while right < left + WINDOW_SIZE and right < len(data):
                current_chunk = data[right]
                packet = build_sender_packet(start_seq, right, current_chunk, True, right == len(data) - 1)
                self.receiver_socket.sendto(packet, self.receiver_address)
                right += 1
                count = 0

            print("Left:", left, "Right:", right)
            if left < right:
                start_timer()

            r, _, _ = select.select([self.receiver_socket], [], [], time_left())
            if r:
                ack_bytes, addr = self.receiver_socket.recvfrom(1024)
                if addr != self.receiver_address:
                    print(f"Received ACK from unknown address compared to {self.receiver_address}:", addr)
                    continue
                
                metadata = parse_ack(ack_bytes)
                
                if not check_ack_corrupt(metadata):
                    print("Received corrupted ACK:", metadata)
                    continue

                ack_no = metadata[ACK_SEQUENCE]
                flag = metadata[ACK_FLAGS]
                ack_offset = get_offset_from_seq(ack_no)

                if ack_offset >= left:
                    print(f"Received ACK for seq {ack_offset}, sliding window")
                    ack_no = min(ack_offset, len(data)) # defensive programming
                    left = ack_offset
                    
                    if left == right: 
                        stop_timer()

                if self.should_stop(flag, ack_offset, left, right):
                    print("Received stop signal from receiver, ending transmission.")
                    break
            elif count < SENDER_RETRY_LIMIT:
                print(f"Timeout occurred, resending packets from seq {left} to {right} count = {count}")
                count += 1
                self.resend_range(start_seq, left, right, data)
                retick_timer()
            else:
                print("Maximum resend attempts reached, ignore packet.")
                left += 1
    
    def resend_range(self, start_seq: int, left: int, right: int, data: list[bytes]) -> None:
        for offset in range(left, right):
            current_chunk = data[offset]
            packet = build_sender_packet(start_seq, offset, current_chunk, True, offset == len(data) - 1)
            self.receiver_socket.sendto(packet, self.receiver_address)

    def should_stop(self, flag: int, ack_offset: int, left: int, right: int) -> bool:
        if ack_offset < left or ack_offset > right:
            print(f"Received out-of-window ACK {ack_offset}, ignore")
            return False

        return flag == 1