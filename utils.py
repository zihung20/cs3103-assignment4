import csv
from pathlib import Path
import time, struct, zlib
from config import FOUR_BYTES_MASK, TWO_BYTES_MASK, ONE_BYTES_MASK, SENDER_HEADER_FORMAT, RECEIVER_ACK_FORMAT, \
    ACK_FLAGS, ACK_CHECKSUM, ACK_SEQUENCE, ACK_TIMESTAMP, SENDER_CHANNEL, SENDER_FLAGS, SENDER_SEQ, \
        SENDER_LENGTH, SENDER_TIMESTAMP

# Utility functions for packet constructing and parsing
def get_current_timestamp():
    return int(time.monotonic_ns() // 1_000_000) & FOUR_BYTES_MASK  # in milliseconds, ensure within 4 bytes

def get_time_passed(timestamp):
    time_now = get_current_timestamp()
    timestamp = timestamp & FOUR_BYTES_MASK
    return (time_now - timestamp) & FOUR_BYTES_MASK  # wrap-safe subtraction

def checksum(packet:bytes) -> int:
    return zlib.crc32(packet)

def ms_to_seconds(ms: int) -> float:
    return ms / 1000.0

def build_sender_packet(seq_no: int, payload, is_reliable: bool, is_last: bool):
    """channel (8 bits) | flags(8 bits)|
       seq (16 bits) | len(16 bits)|
       checksum(32 bits) | timestamp(32 bits)

       every value is safe by masking with appropriate bit masks
    """
    payload = bytes(payload)
    
    channel = (1 if is_reliable else 0) & 0xFF
    flags = (1 if is_last else 0) & 0xFF
    checksum_val = 0
    seq_no = seq_no & TWO_BYTES_MASK
    payload_size = len(payload) & TWO_BYTES_MASK
    timestamp_ms = get_current_timestamp()

    temp_header = struct.pack(SENDER_HEADER_FORMAT, channel, flags, seq_no, payload_size, checksum_val, timestamp_ms)
    checksum_val = checksum(temp_header + payload)

    final_header = struct.pack(SENDER_HEADER_FORMAT, channel, flags, seq_no, payload_size, checksum_val, timestamp_ms)

    return final_header + payload

def parse_packet(packet: bytes):
    header_size = struct.calcsize(SENDER_HEADER_FORMAT)
    metadata = struct.unpack(SENDER_HEADER_FORMAT, packet[:header_size])
    payload = packet[header_size:]

    return metadata, payload

def check_sender_packet(metadata, payload) -> bool:
    received_checksum = metadata[4]
    
    temp_header = struct.pack(SENDER_HEADER_FORMAT, metadata[SENDER_CHANNEL], metadata[SENDER_FLAGS], 
                              metadata[SENDER_SEQ], metadata[SENDER_LENGTH], 0, metadata[SENDER_TIMESTAMP])
    computed_checksum = checksum(temp_header + payload)

    return received_checksum == computed_checksum

def generate_ack(sequence:int, to_stop:bool, sender_timestamp:int) -> bytes:
    """flags (8bit) | ack sequence (16 bits) | checksum (32 bits) | timestamp (32 bits)"""
    flags = (1 if to_stop else 0) & ONE_BYTES_MASK
    sequence = sequence & TWO_BYTES_MASK
    checksum_val = 0
    
    temp_ack = struct.pack(RECEIVER_ACK_FORMAT, flags, sequence, checksum_val, sender_timestamp)
    checksum_val = checksum(temp_ack)

    final_ack = struct.pack(RECEIVER_ACK_FORMAT, flags, sequence, checksum_val, sender_timestamp)
    return final_ack

def parse_ack(ack:bytes):
    metadata = struct.unpack(RECEIVER_ACK_FORMAT, ack)
    return metadata

def check_ack_corrupt(metadata:tuple) -> bool:
    received_checksum = metadata[ACK_CHECKSUM]
    temp_ack = struct.pack(RECEIVER_ACK_FORMAT, metadata[ACK_FLAGS], metadata[ACK_SEQUENCE], 0, metadata[ACK_TIMESTAMP])
    computed_checksum = checksum(temp_ack)
    return received_checksum == computed_checksum


def generate_stats(jitters:list, throughputs:list, latency:list, packet_received: int, total_packet: int, time_stamps:list):
    average_jitters = round(sum(jitters) / len(jitters), 4) if len(jitters) != 0 else 0
    average_throughputs = round(sum(throughputs) / len(throughputs), 4) if len(throughputs) != 0 else 0
    average_latency = round(sum(latency) / len(latency), 4) if len(latency) != 0 else 0
    packet_delivery_ratio = round(packet_received / total_packet, 4) if total_packet != 0 else 0

    first_time = min(time_stamps)

    max_jitter, min_jitter = round(max(jitters),4), round(min(jitters),4)
    max_throughtput, min_throughput = round(max(throughputs), 4), round(min(throughputs), 4)
    max_latency, min_latency = round(max(latency),4), round(min(latency),4)
    t = [i - first_time for i in time_stamps]
    rows = [[jitters[i], throughputs[i], latency[i], t[i]] for i in range(len(jitters))]

    out_path = Path("statistics/receiver_stats.csv")
    
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["jitter", "throughput", "latency", "time stamps"])
            writer.writerows(rows)
    except PermissionError as e:
        print(f"No permission for {out_path}: {e}")
    except FileNotFoundError as e:
        print(f"Parent directory missing: {e}")

    try:
        out_path = Path("statistics/summaries.txt")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", newline="", encoding="utf-8") as f:
            text = (
                f"                  min / mean / max \n"
                f"jitter        :{min_jitter} / {average_jitters} / {max_jitter}\n"
                f"throughput    :{min_throughput} / {average_throughputs} / {max_throughtput}\n"
                f"latency       :{min_latency} / {average_latency} / {max_latency}\n"
                "\n"
                f"packets received          :{packet_received} \n"
                f"expected total packets    :{total_packet} \n"
                f"packet delivery ratio     :{packet_delivery_ratio} \n"
            )
            f.write(text)
    except PermissionError as e:
        print(f"No permission for {out_path}: {e}")
    except FileNotFoundError as e:
        print(f"Parent directory missing: {e}")

def generate_sender_stats(rtts: list):
    out_path = Path("statistics/sender_stats.csv")
        
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["RTT (ms)"])
            for rtt in rtts:
                writer.writerow([rtt])    
    except PermissionError as e:
        print(f"No permission for {out_path}: {e}")
    except FileNotFoundError as e:
        print(f"Parent directory missing: {e}")
    pass