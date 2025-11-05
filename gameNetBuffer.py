class GameNetBuffer:
    def __init__(self):
        self.buffer = {}
        self.offset = 0

    def add_packet(self, seq: int, packet: bytes):
        self.buffer[seq] = packet

    def get_ordered_packets(self) -> list[bytes]:
        return [self.buffer[seq] for seq in sorted(self.buffer.keys())]

    def reset_buffer(self):
        self.buffer = {}

    def get_next_expected_sequence(self):
        if not self.buffer:
            return 0
        
        start_seq = min(self.buffer.keys()) & 0xFF00

        for seq in sorted(self.buffer.keys()):
            seq_offset = seq & 0x00FF
            if seq_offset < self.offset:
                continue
            elif seq_offset == self.offset:
                self.offset += 1
            else:
                break

        return (start_seq & 0xFF00) + (self.offset & 0x00FF)
    
    def skip_current_offset(self):
        self.offset += 1
