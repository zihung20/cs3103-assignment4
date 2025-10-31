import os

HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", 4433))
HEADER_FORMAT = "!HHI"  # seq_no (2 bytes), payload_size (2 bytes), timestamp_ms (4 bytes)
MESSAGE_STRING = "utf-8"  # haven't used, in case any encoding error
TIME_LIMIT_MS = 200

TWO_BYTES_MASK = 0xFFFF
FOUR_BYTES_MASK = 0xFFFFFFFF

# packet metadata fields
METADATA_SEQ_NO = 0
METADATA_PAYLOAD_SIZE = 1
METADATA_TIMESTAMP_MS = 2

reliable_services = ["connect", "message", "action", "heartbeat", "file_transfer"]
unreliable_services = ["voice_call", "video_call", "sensor_update", "chat_reaction"]
