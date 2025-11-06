from config import TWO_BYTES_MASK

class GameNetBuffer:
    def __init__(self, callback_fn=None):
        self.buffer = {}
        self.offset = 0
        self.callback_fn = callback_fn

    def add_packet(self, seq: int, packet: bytes):
        
        self.buffer[seq] = packet
        while self.offset in self.buffer:
            if self.callback_fn:
                self.callback_fn(self.buffer[self.offset])
            self.offset += 1

    def get_ordered_packets(self) -> list[bytes]:
        return [self.buffer[seq] for seq in sorted(self.buffer.keys())]

    def get_next_expected_sequence(self):
        return self.offset & TWO_BYTES_MASK
    
    def skip_current_offset(self):
        self.offset += 1

    def exist(self, seq: int):
        return seq in self.buffer
    
    def get_len(self):
        return len(self.buffer)
