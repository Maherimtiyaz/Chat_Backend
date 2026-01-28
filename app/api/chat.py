# app/api/chat.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.message import Message
from app.core.security import verify_token  # your JWT verification function

router = APIRouter(prefix="/chat", tags=["Chat"])

# ----------------------------
# ConnectionManager for WebSocket rooms
# ----------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append(websocket)

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.active_connections and websocket in self.active_connections[room]:
            self.active_connections[room].remove(websocket)

    async def broadcast(self, room: str, message: dict):
        for connection in self.active_connections.get(room, []):
            try:
                await connection.send_json(message)
            except:
                pass  # fail gracefully if WS is closed

manager = ConnectionManager()

# ----------------------------
# WebSocket endpoint
# ----------------------------
@router.websocket("/ws")
async def chat_ws(websocket: WebSocket, room: str, db: Session = Depends(get_db)):
    # Extract JWT from header
    auth_header = websocket.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        await websocket.accept()
        await websocket.send_json({"error": "Missing or invalid Authorization header"})
        await websocket.close(code=1008)
        return

    token = auth_header.split(" ")[1]
    user = verify_token(token)
    if not user:
        await websocket.accept()
        await websocket.send_json({"error": "Invalid token"})
        await websocket.close(code=1008)
        return

    # Connect WebSocket to room
    await manager.connect(websocket, room)
    await websocket.send_json({"info": f"Connected as {user} to room '{room}'"})

    try:
        while True:
            data = await websocket.receive_text()

            # Save message to DB
            try:
                db_message = Message(
                    username=user,
                    user_id=0,
                    content=data,
                    room=room
                )
                db.add(db_message)
                db.commit()
            except Exception as e:
                await websocket.send_json({"error": f"DB error: {str(e)}"})
                continue

            # Broadcast to room
            await manager.broadcast(room, {
                "room": room,
                "sender": user,
                "message": data
            })

    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
        await manager.broadcast(room, {"info": f"{user} left the room"})
