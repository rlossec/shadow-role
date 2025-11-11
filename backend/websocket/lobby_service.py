from sqlalchemy.ext.asyncio import AsyncSession
from websocket.connexion_manager import ConnexionManager
from repositories.lobby_repository import LobbyRepository


class LobbyService:
    def __init__(self, db: AsyncSession, websocket_manager: ConnexionManager):
        self.db = db
        self.lobby_repo = LobbyRepository(db)
        self.websocket_manager = websocket_manager

    async def join_lobby(self, sid: str, lobby_id: str):
        user = self.websocket_manager.active_users.get(sid)
        await self.websocket_manager.join_lobby(sid, lobby_id)

        ## Ajouter en db
        # await self.lobby_repo.add_player(lobby_id, user.id)

        await self.websocket_manager.broadcast("user_joined", {"user": user.model_dump()}, lobby_id)
