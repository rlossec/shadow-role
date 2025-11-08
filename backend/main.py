from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import socketio

from contextlib import asynccontextmanager

from websocket.server import sio_server
from core.config import settings

from db.database import create_db_and_tables, close_db

from api import auth_router, game_router, lobby_router, player_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield
    await close_db()


# Créer l'application FastAPI
fastapi_app = FastAPI(
    title="Shadow Role API",
    description="API for the Shadow Role web app",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configuration CORS
allowed_origins = settings.ALLOWED_ORIGINS if settings.ALLOWED_ORIGINS else ["*"]
allowed_methods = settings.ALLOWED_METHODS.split(",") if isinstance(settings.ALLOWED_METHODS, str) else ["*"]
allowed_headers = settings.ALLOWED_HEADERS.split(",") if isinstance(settings.ALLOWED_HEADERS, str) else ["*"]

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=allowed_methods,
    allow_headers=allowed_headers,
)

fastapi_app.include_router(auth_router)
fastapi_app.include_router(game_router)
fastapi_app.include_router(lobby_router)
fastapi_app.include_router(player_router)

# Enregistrer le serveur Socket.IO
socket_app = socketio.ASGIApp(sio_server)
fastapi_app.mount("/ws", socket_app)

@fastapi_app.get("/")
def home():
    return {"message": "Shadow Role API", "version": "0.1.0"}


# Alias pour uvicorn (main:app)
app = fastapi_app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=int(settings.API_PORT),
        reload=settings.DEBUG,
    )

