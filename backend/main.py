from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter

from contextlib import asynccontextmanager

from websocket.socket_server import sio_app
from core.config import settings

from db.database import create_db_and_tables, close_db

from api import auth_router, game_router, lobby_router, player_router, mission_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield
    await close_db()


# Créer l'application FastAPI
app = FastAPI(
    title="Shadow Role API",
    description="API for the Shadow Role web app",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configuration CORS
# settings.ALLOWED_ORIGINS est déjà une liste grâce au validator
allowed_origins = settings.ALLOWED_ORIGINS if settings.ALLOWED_ORIGINS else ["*"]
allowed_methods = settings.ALLOWED_METHODS.split(",") if isinstance(settings.ALLOWED_METHODS, str) else ["*"]
allowed_headers = settings.ALLOWED_HEADERS.split(",") if isinstance(settings.ALLOWED_HEADERS, str) else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=allowed_methods,
    allow_headers=allowed_headers,
)

# Créer un router API principal avec le préfixe depuis les settings
api_router = APIRouter(prefix=settings.API_PREFIX)

# Inclure tous les routers sous le router API principal
api_router.include_router(auth_router)
api_router.include_router(game_router)
api_router.include_router(lobby_router)
api_router.include_router(player_router)
api_router.include_router(mission_router)

# Inclure le router API principal dans l'application
app.include_router(api_router)

# Route racine FastAPI
@app.get("/")
def home():
    return {"message": "Shadow Role API", "version": "0.1.0"}


# Combiner FastAPI et Socket.IO dans une seule application ASGI
app.mount(settings.SOCKETIO_PATH, sio_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=int(settings.API_PORT),
        reload=settings.DEBUG,
    )
