from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.core.security import verify_token  # Your JWT verification function

# Create a router with /chat prefix
router = APIRouter(prefix="/chat", tags=["Chat"])

# ----------------------------------------
# ConnectionManager: handles WebSocket connections per room
# ----------------------------------------
class ConnectionManager:
    def __init__(self):
        """
        Dictionary mapping room names to a list of active WebSocket connections.
        Example:
            {
                "general": [ws1, ws2],
                "random": [ws3]
            }
        """
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str):
        """Accept WebSocket connection and add it to the specified room"""
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append(websocket)

    def disconnect(self, websocket: WebSocket, room: str):
        """Remove WebSocket connection from the specified room"""
        if room in self.active_connections and websocket in self.active_connections[room]:
            self.active_connections[room].remove(websocket)

    async def broadcast(self, room: str, message: dict):
        """
        Broadcast a message to all clients in the specified room.
        Message is sent as JSON for better structure (room, sender, message).
        """
        for connection in self.active_connections.get(room, []):
            await connection.send_json(message)

# Instantiate a single manager to track all rooms
manager = ConnectionManager()

# ----------------------------------------
# Secure WebSocket endpoint
# ----------------------------------------
@router.websocket("/ws")
async def chat_ws(websocket: WebSocket, room: str = Query(...)):
    """
    WebSocket endpoint for a chat room.
    Requires a JWT token in the "Authorization" header.
    Query Parameter:
        - room: name of the chat room
    """

    # Extract JWT token from headers
    auth_header = websocket.headers.get("Authorization")


    if not auth_header or not auth_header.startswith("Bearer "):        # Close connection if no token provided
        await websocket.close(code=1008)  # Policy violation
        return
    
    token = auth_header.split(" ")[1]

    # Verify token and get user info
    user = verify_token(token)
    if not user:
        # Close connection if token is invalid
        await websocket.close(code=1008)
        return

    # Add client to the room
    await manager.connect(websocket, room)

    try:
        while True:
            # Wait for message from client
            data = await websocket.receive_text()

            # Prepare message payload
            message = {
                "room": room,
                "sender": user["username"],
                "message": data,
            }

            # Broadcast message to all clients in the same room
            await manager.broadcast(room, message)

    except WebSocketDisconnect:
        # Remove client when they disconnect
        manager.disconnect(websocket, room)
