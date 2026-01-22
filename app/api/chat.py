from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.security import verify_ws_token
from app.core.manager import ConnectionManager

router = APIRouter(prefix="/chat", tags=["Chat"])

router = APIRouter()
manager = ConnectionManager()

# Manager for WebSocket connections

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# WebSocket endpoint

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            message = await websocket.receive_text()
            await manager.broadcast(message)

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Secure WebSocket endpoint

@router.websocket("/chat/ws")
async def chat_ws(websocket: WebSocket):
    token = websocket.query_params.get("token")


    if not token:
        await websocket.close(code=1008)
        return # Close connection if no token
    
    # Verify token
    username = verify_ws_token(token)
    if not username:
        await websocket.close(code=1008)
        return
    
    # Connect to WebSocket
    await manager.connect(websocket, username)

    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{username}: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    
    