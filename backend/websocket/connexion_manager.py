import uuid

from typing import Dict

from core.config import settings
from repositories.jwt_repository import JWTRepository

from pydantic import BaseModel
from db.database import async_session_maker
from repositories.user_repository import UserRepository

class WebSocketUser(BaseModel):
    id: str
    username: str



class ConnexionManager:
    def __init__(self, sio_server):
        self.sio_server = sio_server
        self.active_users: Dict[str, WebSocketUser] = {}    # sid     -> WebSocketUser
        self.user_lobbies: Dict[str, str] = {}              # user_id -> lobby_id
        self.jwt_repository = JWTRepository(
            secret_key=settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
            refresh_secret_key=settings.REFRESH_SECRET_KEY or settings.SECRET_KEY,
        )
        self.user_repository = UserRepository(async_session_maker())

    async def authenticate(self, token: str) -> WebSocketUser:
        """ Décode le token et retourne l'utilisateur """
        try:
            payload = self.jwt_repository.decode_token(token)
            user_id = uuid.UUID(str(payload["sub"]))
            user = await self.user_repository.get_user(user_id)
            if user is None:
                raise ConnectionRefusedError("User not found")
            return WebSocketUser(id=str(user.id), username=user.username)
        except Exception as exc:
            print(f"Error decoding token: {exc}")
            raise ConnectionRefusedError("Invalid or expired token") from exc


    async def register_connection(self, sid: str, user: WebSocketUser):
        """ Enregistre la connexion de l'utilisateur """
        self.active_users[sid] = user
        print(f"✅ {user.username} connected (SID={sid})")
    
    async def remove_connection(self, sid: str):
        """ Enlève la connexion de l'utilisateur """
        if sid in self.active_users:
            user = self.active_users.pop(sid, None)
            await self.leave_lobby(sid, self.user_lobbies.get(user.id, None))

    async def join_lobby(self, sid: str, lobby_id: str):
        await self.sio_server.save_session(sid, {"lobby_id": lobby_id})
        await self.sio_server.enter_room(sid, lobby_id)
        self.user_lobbies[self.active_users[sid].id] = lobby_id
        print(f"✅ {self.active_users[sid].username} joined lobby {lobby_id} (SID={sid})")
    
    async def leave_lobby(self, sid: str, lobby_id: str):
        if lobby_id:
            await self.sio_server.leave_room(sid, lobby_id)

    async def broadcast(self, event: str, data: dict, lobby_id: str):
        await self.sio_server.emit(event, data, room=lobby_id)

    async def send_to(self, sid: str, event: str, data: dict):
        await self.sio_server.emit(event, data, to=sid)
