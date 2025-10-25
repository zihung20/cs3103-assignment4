server_messages = [
    {
        "type": "ack",
        "msg": "connected",
        "server_time": 1730000001
    },
    {
        "type": "world_state",
        "players": [
            {"id": "player123", "x": 25, "y": 47, "hp": 98},
            {"id": "enemy42", "x": 32, "y": 44, "hp": 60}
        ],
        "timestamp": 1730000005
    },
    {
        "type": "event",
        "event": "hit",
        "attacker": "player123",
        "target": "enemy42",
        "damage": 15,
        "timestamp": 1730000006
    },
    {
        "type": "disconnect_notice",
        "msg": "Server shutting down in 5s",
        "timestamp": 1730000010
    }
]
