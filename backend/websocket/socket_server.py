
import socketio
from db.database import async_session_maker
from websocket.lobby_service import LobbyService
from websocket.connexion_manager import ConnexionManager
from core.config import settings

sio_server = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[],
)


sio_app = socketio.ASGIApp(
    socketio_server=sio_server,
    socketio_path=settings.SOCKETIO_PATH,
)

db = async_session_maker()
manager = ConnexionManager(sio_server)
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
async def disconnect(sid):
    await manager.remove_connection(sid)
    print(f"🔌 SID={sid} disconnected")



# --- Gestion des événements de jeu ---

@sio_server.event
async def join_lobby(sid, data):
    lobby_id = data.get("lobby_id")
    await lobby_service.join_lobby(sid, lobby_id)



__all__ = ["sio_server", "sio_app"]