import time

mock_client_msgs = [
    # Reliable
    {"seq": 1, "service": "connect", "reliability": "reliable",
     "payload": {"user": "alice", "status": "login", "ts": time.time()}},

    {"seq": 2, "service": "message", "reliability": "reliable",
     "payload": {"from": "alice", "to": "bob", "msg": "hi!", "ts": time.time()}},

    {"seq": 3, "service": "action", "reliability": "reliable",
     "payload": {"player": "alice", "act": "jump", "x": 3, "y": 7}},

    {"seq": 4, "service": "heartbeat", "reliability": "reliable",
     "payload": {"user": "alice", "ping_id": 101, "ts": time.time()}},

    {"seq": 5, "service": "file_transfer", "reliability": "reliable",
     "payload": {"file": "map_chunk_1.dat", "size": 4096, "hash": "a1b2c3"}},

    # Unreliable
    {"seq": 6, "service": "voice_call", "reliability": "unreliable",
     "payload": {"user": "alice", "frame_id": 24, "bytes": "<40ms audio frame>"}},

    {"seq": 7, "service": "voice_call", "reliability": "unreliable",
     "payload": {"user": "alice", "frame_id": 25, "bytes": "<40ms audio frame>"}},

    {"seq": 8, "service": "video_call", "reliability": "unreliable",
     "payload": {"user": "alice", "frame_id": 102, "res": "640x480", "chunk": "<I-frame data>"}},

    {"seq": 9, "service": "sensor_update", "reliability": "unreliable",
     "payload": {"device": "gyro", "x": 0.12, "y": 0.42, "z": -0.08, "ts": time.time()}},

    {"seq": 10, "service": "chat_reaction", "reliability": "unreliable",
     "payload": {"from": "bob", "to": "alice", "emoji": "👍", "msg_id": 873}},
]

mock_server_responses = [
    {"seq": 1, "service": "connect", "response": {"ack": "login_ok", "session_id": "S42"}},
    {"seq": 2, "service": "message", "response": {"ack": "msg_rcvd", "id": 873}},
    {"seq": 3, "service": "action", "response": {"ack": "action_applied", "frame": 391}},
    {"seq": 4, "service": "heartbeat", "response": {"ack": "pong", "ping_id": 101}},
    {"seq": 5, "service": "file_transfer", "response": {"ack": "chunk_saved", "status": "ok"}},

    {"seq": 6, "service": "voice_call", "response": {"relay": "audio_frame", "frame_id": 24}},
    {"seq": 7, "service": "voice_call", "response": None},  # simulate drop/loss
    {"seq": 8, "service": "video_call", "response": {"relay": "video_frame", "frame_id": 102}},
    {"seq": 9, "service": "sensor_update", "response": {"relay": "sensor_ok"}},
    {"seq": 10, "service": "chat_reaction", "response": {"ack": "reaction_seen"}},
]