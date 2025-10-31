import time, struct, zlib
from config import FOUR_BYTES_MASK, TWO_BYTES_MASK, SENDER_HEADER_FORMAT, RECEIVER_ACK_FORMAT, \
    PAYLOAD_SIZE_BYTES, ACK_CHECKSUM, ACK_SEQUENCE, ACK_TIMESTAMP, SENDER_CHANNEL, SENDER_FLAGS, SENDER_SEQ, \
        SENDER_LENGTH, SENDER_TIMESTAMP

# Utility functions for packet handling, mostly about packet related operations
def get_current_timestamp():
    return int(time.monotonic_ns() // 1_000_000) & FOUR_BYTES_MASK  # in milliseconds, ensure within 4 bytes

def get_time_passed(timestamp):
    time_now = get_current_timestamp()
    timestamp = timestamp & FOUR_BYTES_MASK
    return (time_now - timestamp) & FOUR_BYTES_MASK  # wrap-safe subtraction

def checksum(packet:bytes) -> int:
    return zlib.crc32(packet)

def generate_chunks(data:bytes) -> list[bytes]:
    chunks: list[bytes] = []

    for i in range (0, len(data), PAYLOAD_SIZE_BYTES):
        chunk = data[i: i + PAYLOAD_SIZE_BYTES]
        chunks.append(chunk)
    
    return chunks

def build_sender_packet(seq_no: int, payload, is_reliable:bool, is_last: bool):
    """channel (8 bits) | flags(8 bits)|
       seq (16 bits) | len(16 bits)|
       checksum(32 bits) | timestamp(32 bits)

       every value is safe by masking with appropriate bit masks
    """
    payload = bytes(payload)
    
    channel = (1 if is_reliable else 0) & 0xFF
    flags = (1 if is_last else 0) & 0xFF
    checksum_val = 0
    seq_no = seq_no & TWO_BYTES_MASK  # ensure within 2 bytes
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

def generate_ack(sequence:int) -> bytes:
    """ack sequence (16 bits) | checksum (32 bits) | timestamp (32 bits)"""
    sequence = sequence & TWO_BYTES_MASK
    checksum_val = 0
    timestamp_ms = get_current_timestamp() & FOUR_BYTES_MASK

    temp_ack = struct.pack(RECEIVER_ACK_FORMAT, sequence, checksum_val, timestamp_ms)
    checksum_val = checksum(temp_ack)

    final_ack = struct.pack(RECEIVER_ACK_FORMAT, sequence, checksum_val, timestamp_ms)
    return final_ack

def parse_ack(ack:bytes):
    metadata = struct.unpack(RECEIVER_ACK_FORMAT, ack)
    return metadata

def check_ack_corrupt(metadata:tuple) -> bool:
    received_checksum = metadata[ACK_CHECKSUM]
    temp_ack = struct.pack(RECEIVER_ACK_FORMAT, metadata[ACK_SEQUENCE], 0, metadata[ACK_TIMESTAMP])
    computed_checksum = checksum(temp_ack)
    return received_checksum == computed_checksum