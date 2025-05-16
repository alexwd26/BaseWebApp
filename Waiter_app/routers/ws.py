from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

ws_router = APIRouter()

# Allow CORS for local dev
# ws_router.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Restrict in production!
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Store connected clients
clients = []

@ws_router.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()  # Optionally handle incoming messages
            # For demo, just echo or ignore
    except WebSocketDisconnect:
        clients.remove(websocket)

# Utility to broadcast to all clients
async def broadcast_notification(message: str):
    for ws in clients:
        await ws.send_text(message)
