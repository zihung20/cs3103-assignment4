HOST="localhost"
PORT=4433
HEADER_FORMAT="!H H I"
MESSAGE_STRING="utf-8"# haven't used, in case any encoding error
TIME_LIMIT_MS=200

reliable_services = ["connect", "message", "action", "heartbeat", "file_transfer"]
unreliable_services = ["voice_call", "video_call", "sensor_update", "chat_reaction"]
