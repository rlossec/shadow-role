
from uuid import UUID
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload


from models import Game, GameType, Tag
from schemas import GameCreate, GameUpdate


class GameRepository:
    """Repository for the game model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_games(self, skip: int = 0, limit: int = 100) -> list[Game]:
        """Get all games with pagination"""
        result = await self.db.execute(
            select(Game)
            .options(selectinload(Game.tags))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_game(self, game_data: GameCreate) -> Game:
        """Create a new game"""
        # Exclure tags du dump car c'est une relation many-to-many
        data = game_data.model_dump(exclude={"tags"})
        
        game = Game(**data)
        self.db.add(game)
        await self.db.flush()  # Flush pour avoir l'ID du jeu
        
        # Gérer les tags séparément (même si liste vide ou None)
        tags_list = game_data.tags if game_data.tags is not None else []
        await self._sync_game_tags(game, tags_list)
        
        await self.db.commit()
        # Recharger avec les tags pour la réponse
        result = await self.db.execute(
            select(Game)
            .options(selectinload(Game.tags))
            .where(Game.id == game.id)
        )
        game = result.scalar_one()
        return game

    async def get_game(self, game_id: UUID) -> Game | None:
        """Get a game by ID"""
        result = await self.db.execute(
            select(Game)
            .options(selectinload(Game.tags))
            .where(Game.id == game_id)
        )
        return result.scalar_one_or_none()

    async def update_game(self, game: Game, game_data: GameUpdate) -> Game:
        """Update the provided game with the given data."""
        # Exclure tags du dump car c'est une relation many-to-many
        data = game_data.model_dump(exclude_unset=True, exclude={"tags"})
        for field, value in data.items():
            setattr(game, field, value)
        
        # Gérer les tags séparément si fournis
        dumped_data = game_data.model_dump(exclude_unset=True)
        if "tags" in dumped_data:
            await self._sync_game_tags(game, game_data.tags or [])
        
        await self.db.commit()
        # Recharger avec les tags
        result = await self.db.execute(
            select(Game)
            .options(selectinload(Game.tags))
            .where(Game.id == game.id)
        )
        game = result.scalar_one()
        return game

    async def delete_game(self, game_id: UUID) -> None:
        """Delete the provided game."""
        game = await self.get_game(game_id)
        if game:
            await self.db.delete(game)
            await self.db.commit()
            return True
        return False

    async def get_game_with_missions(self, game_id: UUID) -> Game | None:
        """Get a game missions"""
        result = await self.db.execute(
            select(Game)
            .options(selectinload(Game.missions))
            .where(Game.id == game_id)
        )
        return result.scalar_one_or_none()
    
    async def _sync_game_tags(self, game: Game, tag_names: List[str]) -> None:
        """Synchronise les tags d'un jeu avec une liste de noms de tags"""
        # Charger les tags avec selectinload pour s'assurer qu'ils sont accessibles
        result = await self.db.execute(
            select(Game)
            .options(selectinload(Game.tags))
            .where(Game.id == game.id)
        )
        game_with_tags = result.scalar_one()
        
        # Vider les tags existants
        game_with_tags.tags.clear()
        
        # Si aucune liste de tags ou liste vide, on laisse les tags vides
        if not tag_names:
            await self.db.flush()
            return
        
        # Récupérer ou créer les tags
        tags_to_add = []
        for tag_name in tag_names:
            if not tag_name or not tag_name.strip():
                continue
            
            tag_name = tag_name.strip()
            
            # Chercher le tag existant
            result = await self.db.execute(
                select(Tag).where(Tag.name == tag_name)
            )
            tag = result.scalar_one_or_none()
            
            # Créer le tag s'il n'existe pas
            if not tag:
                tag = Tag(name=tag_name)
                self.db.add(tag)
                await self.db.flush()
            
            # Vérifier que le tag n'est pas déjà dans la liste (éviter les doublons)
            if tag not in tags_to_add:
                tags_to_add.append(tag)
        
        # Ajouter tous les tags en une fois à la relation
        game_with_tags.tags.extend(tags_to_add)
        await self.db.flush()
