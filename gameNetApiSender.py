from socket import *
from utils import generate_chunks, parse_ack, check_ack_corrupt, build_sender_packet
from config import TIME_LIMIT_MS, WINDOW_SIZE, SENDER_RETRY_LIMIT, ACK_SEQUENCE, ACK_FLAGS
import select, time

class GameSender:
    def __init__(self, server_name:str, server_port:int):
        self.server_name = server_name
        self.server_port = server_port
        self.server_address = (server_name, server_port)
        self.seq_no = 0
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)
        print(f"Send to {self.server_address}")

    def send_data(self, data:bytes, is_reliable:bool) -> None:
        chunks = generate_chunks(data)
        self.seq_no += len(chunks)
        
        if is_reliable:
            self.send_reliable_packets(chunks)
        else:
            self.send_unreliable_packets(chunks)

    def send_unreliable_packets(self, chunks:list[bytes]) -> None:
        start_seq = self.seq_no - len(chunks)
        for i, current_chunk in enumerate(chunks):
            seq = i + start_seq
            packet = build_sender_packet(seq, current_chunk, False, seq == self.seq_no - 1)
            self.clientSocket.sendto(packet, self.server_address)

    def send_reliable_packets(self, chunks:list[bytes]) -> None:
        buffer = {}
        first_seq = self.seq_no - len(chunks)
        left = first_seq
        right = first_seq
        last_seq_exclusive = self.seq_no
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
        while left < last_seq_exclusive:

            while right < left + WINDOW_SIZE and right < last_seq_exclusive:
                current_chunk = chunks[right - first_seq]
                param = (right, current_chunk, True, right == last_seq_exclusive - 1) # for future reconstruction
                packet = build_sender_packet(*param)
                buffer[right] = param
                self.clientSocket.sendto(packet, self.server_address)
                right += 1
                count = 0

            if left < right:
                start_timer()

            r, _, _ = select.select([self.clientSocket], [], [], time_left())
            if r:
                ack_bytes, addr = self.clientSocket.recvfrom(1024)
                if addr != self.server_address: 
                    print(f"Received ACK from unknown address compared to {self.server_address}:", addr)
                    continue
                metadata = parse_ack(ack_bytes)
                if not check_ack_corrupt(metadata):
                    print("Received corrupted ACK:", metadata)
                    continue
                elif self.should_stop(metadata, left, right):
                    print("Received stop signal from receiver, terminating transmission.")
                    break

                ack_no = metadata[ACK_SEQUENCE]
                if ack_no > left:
                    print(f"Received ACK for seq {ack_no}, sliding window")
                    ack_no = min(ack_no, last_seq_exclusive) # defensive programming
                    left = ack_no
                    for seq in list(buffer.keys()):
                        if seq < ack_no: buffer.pop(seq, None)
                    
                    if left == right: 
                        stop_timer()
                    else:
                        retick_timer()
            elif count < SENDER_RETRY_LIMIT:
                print(f"Timeout occurred, resending packets from seq {left} to {right} count={count}")
                count += 1
                self.resend_range(left, right, buffer)
                retick_timer()
            else :
                print("Maximum resend attempts reached, terminating transmission.")
                break
    
    def resend_range(self, start:int, end:int, buffer:dict) -> None:
        for seq in range(start, end):
            param = buffer.get(seq, None)
            if param:
                pkt = build_sender_packet(*param)
                self.clientSocket.sendto(pkt, self.server_address)
    
    def should_stop(self, metadata:tuple, left:int, right:int) -> None:
        ack_seq_no = metadata[ACK_SEQUENCE]
        if ack_seq_no < left or ack_seq_no > right:
            print(f"Received out-of-window ACK {metadata}, ignore")
            return False
    
        # valid ACK within window, set the seq_no to be it so that further packets are sync
        self.seq_no = ack_seq_no
        flags = metadata[ACK_FLAGS]
        return flags == 1