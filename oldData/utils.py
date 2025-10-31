import time, struct
from config import HEADER_FORMAT, METADATA_PAYLOAD_SIZE, FOUR_BYTES_MASK, TWO_BYTES_MASK

def get_current_timestamp():
    return int(time.monotonic_ns() // 1_000_000) & FOUR_BYTES_MASK  # in milliseconds, ensure within 4 bytes

def get_time_passed(timestamp):
    time_now = get_current_timestamp()
    timestamp = timestamp & FOUR_BYTES_MASK
    print("time_now:", time_now, ", timestamp:", timestamp)
    return (time_now - timestamp) & FOUR_BYTES_MASK  # wrap-safe subtraction

def generate_header(seq_no, payload_size):
    seq_no = seq_no & TWO_BYTES_MASK  # ensure within 2 bytes
    payload_size = payload_size & TWO_BYTES_MASK  # ensure within 2 bytes
    timestamp_ms = get_current_timestamp() & FOUR_BYTES_MASK  # ensure within 4 bytes

    header = struct.pack(HEADER_FORMAT, seq_no, payload_size, timestamp_ms)
    return header

def generate_packet(seq_no, payload):
    payload = bytes(payload)
    header = generate_header(seq_no, len(payload))
    packet = header + payload
    return packet
    
def parse_packet(packet):
    header_size = struct.calcsize(HEADER_FORMAT)
    metadata = struct.unpack(HEADER_FORMAT, packet[:header_size])
    payload = packet[header_size:header_size + metadata[METADATA_PAYLOAD_SIZE]]

    return metadata, payload