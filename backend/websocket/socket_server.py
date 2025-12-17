
import socketio
import uuid

from core.config import settings
from db.database import async_session_maker
from websocket.manager import WebSocketManager
from services.lobby_service import LobbyService


# Ne pas configurer CORS ici car FastAPI le gère déjà via son middleware
# Cela évite la duplication des headers CORS qui cause l'erreur
# "The 'Access-Control-Allow-Origin' header contains multiple values"
sio_server = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[],  # Désactivé - FastAPI gère CORS
)


sio_app = socketio.ASGIApp(
    socketio_server=sio_server,
    socketio_path=settings.SOCKETIO_PATH,
)

db = async_session_maker()
manager = WebSocketManager(sio_server)
lobby_service = LobbyService(db, manager)

@sio_server.event
async def connect(sid, environ, auth):
    # Authentification
    token = auth.get("token") if auth else None
    if not token:
        raise ConnectionRefusedError("Authentication required")

    # Rechercher l'utilisateur
    user = await manager.authenticate(token)
    await manager.register_connection(sid, user)


@sio_server.event
async def disconnect(sid, *args):
    await manager.remove_connection(sid)
    print(f"🔌 SID={sid} disconnected")


# --- Gestion des événements de jeu ---

@sio_server.event
async def join_lobby(sid, data):
    lobby_id = data.get("lobby_id")
    await lobby_service.join_lobby(sid, lobby_id)

@sio_server.event
async def register_player(sid, data):
    lobby_id = data.get("lobby_id")
    alias = data.get("alias")
    color = data.get("color")
    print(f"🔍 SID={sid} joining lobby {lobby_id} and alias {alias} and color {color}")
    await lobby_service.register_player(sid, lobby_id, alias, color)


@sio_server.event
async def unregister_player(sid, data):
    lobby_id = data.get("lobby_id")
    user_id = data.get("user_id")
    if not lobby_id or not user_id:
        return
    await lobby_service.unregister_player(str(lobby_id), uuid.UUID(str(user_id)))


@sio_server.event
async def sync_lobby_state(sid, data):
    lobby_id = data.get("lobby_id")
    if lobby_id:
        await lobby_service.sync_lobby_state(sid, uuid.UUID(str(lobby_id)))


__all__ = ["sio_app"]
