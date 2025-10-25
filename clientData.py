client_messages = [
    {
        "type": "connect",
        "client_id": "player123",
        "timestamp": 1730000000,
    },
    {
        "type": "state_update",
        "client_id": "player123",
        "position": {"x": 25, "y": 47},
        "velocity": {"x": 0.4, "y": -0.1},
        "hp": 98,
        "timestamp": 1730000005,
    },
    {
        "type": "action",
        "client_id": "player123",
        "action": "shoot",
        "target": "enemy42",
        "weapon": "laser",
        "timestamp": 1730000006,
    },
    {
        "type": "disconnect",
        "client_id": "player123",
        "reason": "user_exit",
        "timestamp": 1730000010,
    }
]
