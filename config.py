import os, socket

PORT = int(os.getenv("PORT", 4433))
MESSAGE_STRING = "utf-8"  # haven't used, in case any encoding error
TIME_LIMIT_MS = 10000

ONE_BYTES_MASK = 0xFF
TWO_BYTES_MASK = 0xFFFF
FOUR_BYTES_MASK = 0xFFFFFFFF

reliable_services = ["connect", "message", "action", "heartbeat", "file_transfer"]
unreliable_services = ["voice_call", "video_call", "sensor_update", "chat_reaction"]

# new design
SENDER_HEADER_FORMAT = "!BBHHII"
SENDER_CHANNEL      = 0  # 8-bit 1 = reliable, 0 = unreliable
SENDER_FLAGS        = 1  # 8-bit 1 if it's last, 0 otherwise
SENDER_SEQ          = 2  # 16-bit sequence number
SENDER_LENGTH       = 3  # 16-bit payload length
SENDER_CHECKSUM     = 4  # 32-bit CRC/checksum
SENDER_TIMESTAMP    = 5  # 32-bit ms timestamp (send time)
SENDER_RETRY_LIMIT = 5  # max retry count for reliable packets

RECEIVER_ACK_FORMAT = "!HII"
ACK_SEQUENCE    = 0  # 16-bit ACK sequence number
ACK_CHECKSUM    = 1  # 32-bit checksum
ACK_TIMESTAMP   = 2  # 32-bit ms timestamp (receive/send time)

PAYLOAD_SIZE_BYTES = 1186
WINDOW_SIZE = 5

