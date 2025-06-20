from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import logging
import asyncio
from typing import Dict, List
from services.ai.ollama_service import OllamaService
from services.ai.mediapipe_service import MediaPipeService
from services.ai.consciousness_service import ConsciousnessService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="QCYIS Backend",
    description="Quantum Consciousness Yoga Intelligence System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ollama_service = OllamaService()
mediapipe_service = MediaPipeService()
consciousness_service = ConsciousnessService()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected: {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")

    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(json.dumps(message))

manager = ConnectionManager()

@app.websocket("/ws/yoga/{session_id}")
async def yoga_websocket(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message['type'] == 'pose_frame':
                # Process pose with MediaPipe
                pose_result = await mediapipe_service.process_frame(message['data'])
                await manager.send_personal_message({
                    "type": "pose_correction",
                    "data": pose_result
                }, session_id)
            
            elif message['type'] == 'chat_message':
                # Process with Ollama locally
                response = await ollama_service.generate_response(
                    prompt=message['content'],
                    context="yoga_instruction"
                )
                await manager.send_personal_message({
                    "type": "chat_response",
                    "data": response
                }, session_id)
            
            elif message['type'] == 'consciousness_data':
                # Process consciousness data
                consciousness_result = await consciousness_service.analyze_consciousness(message['data'])
                await manager.send_personal_message({
                    "type": "consciousness_analysis",
                    "data": consciousness_result
                }, session_id)
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(session_id)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": {
        "ollama": await ollama_service.health_check(),
        "mediapipe": mediapipe_service.is_ready(),
        "consciousness": consciousness_service.is_ready()
    }}

@app.on_event("startup")
async def startup_event():
    logger.info("Starting QCYIS Backend...")
    await ollama_service.initialize()
    await mediapipe_service.initialize()
    await consciousness_service.initialize()
    logger.info("All services initialized successfully")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
