from fastapi import WebSocket
from typing import Dict

# Connection Manager for WebSocket connections

class ConnectionManager:
    def __init__(self):
        # room_name -> {WebSocket: user_info}
        self.rooms: Dict[str, Dict[WebSocket, dict]] = {}

    async def connect(self, websocket: WebSocket, room: str, user: dict):
        await websocket.accept()

        if room not in self.rooms:
            self.rooms[room] = {}

        self.rooms[room][websocket] = user

    # Disconnect a WebSocket from a room    

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.rooms and websocket in self.rooms[room]:
            del self.rooms[room][websocket]

            if not self.rooms[room]:
                del self.rooms[room]

    # Broadcast a message to all WebSockets in a room

    async def broadcast(self, room: str, message: dict):
        if room not in self.rooms:
            return
        
        for websocket in self.rooms[room]:
            await websocket.sendjson(message)