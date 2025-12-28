
from typing import Optional
import threading

from sqlalchemy.ext.asyncio import AsyncSession

import factory


class BaseFactory(factory.Factory):
    """Base factory pour créer des objets SQLAlchemy de manière asynchrone."""
    
    _session: Optional[AsyncSession] = None
    _sequence_counters = {}  # Compteurs de séquences par factory
    _sequence_lock = threading.Lock()  # Lock pour la thread-safety
    
    class Meta:
        abstract = True
    
    @classmethod
    def set_session(cls, session: AsyncSession):
        """Définir la session de base de données à utiliser."""
        cls._session = session
    
    @classmethod
    def get_session(cls) -> Optional[AsyncSession]:
        """Obtenir la session de base de données."""
        return cls._session
    
    @classmethod
    def _get_sequence_counter(cls, field_name: str) -> int:
        """Obtenir et incrémenter le compteur de séquence pour un champ."""
        key = f"{cls.__name__}.{field_name}"
        with cls._sequence_lock:
            if key not in cls._sequence_counters:
                cls._sequence_counters[key] = 0
            cls._sequence_counters[key] += 1
            return cls._sequence_counters[key]
    
    @classmethod
    def _generate_params(cls, **kwargs):
        """Générer les paramètres pour créer l'objet."""
        params = {}
        for field_name, field in cls._meta.declarations.items():
            # Ignorer les PostGeneration - ils ne sont pas utilisés dans notre implémentation
            if isinstance(field, factory.declarations.PostGeneration):
                continue
            if field_name not in kwargs:
                if isinstance(field, factory.LazyAttribute):
                    params[field_name] = field.evaluate(None, None, {})
                elif isinstance(field, factory.SubFactory):
                    # Pour les SubFactory, on marque comme None pour résolution async
                    params[field_name] = None
                elif isinstance(field, factory.Sequence):
                    # Évaluer la séquence en appelant directement la fonction avec le compteur
                    counter = cls._get_sequence_counter(field_name)
                    # Appeler directement la fonction de la séquence
                    params[field_name] = field.function(counter)
                else:
                    params[field_name] = field
        params.update(kwargs)
        return params
    
    @classmethod
    async def _resolve_subfactories(cls, params):
        """Résoudre les SubFactory de manière asynchrone."""
        resolved_params = {}
        for key, value in params.items():
            if key in cls._meta.declarations:
                field = cls._meta.declarations[key]
                if isinstance(field, factory.SubFactory) and value is None:
                    # Créer l'objet via la SubFactory
                    sub_factory = field.get_factory()
                    resolved_params[key] = await sub_factory.create()
                else:
                    resolved_params[key] = value
            else:
                resolved_params[key] = value
        return resolved_params
    
    @classmethod
    async def _create(cls, model_class, *args, **kwargs):
        """Créer et sauvegarder un objet en base de données de manière asynchrone."""
        if not cls._session:
            raise ValueError(
                f"Session not set for {cls.__name__}. "
                "Call BaseFactory.set_session(session) or use setup_factories(session) first."
            )
        
        # Résoudre les SubFactory
        resolved_kwargs = await cls._resolve_subfactories(kwargs)
        
        # Filtrer les PostGeneration des kwargs (ils ne sont pas utilisés)
        model_kwargs = {}
        for key, value in resolved_kwargs.items():
            if key in cls._meta.declarations:
                field = cls._meta.declarations[key]
                if isinstance(field, factory.declarations.PostGeneration):
                    # Ignorer les PostGeneration
                    continue
            model_kwargs[key] = value
        
        instance = model_class(*args, **model_kwargs)
        cls._session.add(instance)
        await cls._session.commit()
        await cls._session.refresh(instance)
        return instance
    
    @classmethod
    async def create(cls, **kwargs):
        """Créer et sauvegarder un objet en base de données."""
        return await cls._create(cls._meta.model, **cls._generate_params(**kwargs))
    
    @classmethod
    def build(cls, **kwargs):
        """Construire un objet sans le sauvegarder en base de données."""
        params = cls._generate_params(**kwargs)
        # Pour build, on ne résout pas les SubFactory, on les laisse comme None
        # ou on peut créer des objets temporaires
        build_params = {}
        for key, value in params.items():
            if key in cls._meta.declarations:
                field = cls._meta.declarations[key]
                if isinstance(field, factory.SubFactory) and value is None:
                    # Pour build, on crée un objet temporaire
                    sub_factory = field.get_factory()
                    build_params[key] = sub_factory.build()
                else:
                    build_params[key] = value
            else:
                build_params[key] = value
        return cls._meta.model(**build_params)
