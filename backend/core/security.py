from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from core.config import settings


# Configuration pour le hashage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie si le mot de passe en clair correspond au hash.
    
    Args:
        plain_password: Mot de passe en clair
        hashed_password: Mot de passe hashé
        
    Returns:
        True si les mots de passe correspondent
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash un mot de passe avec bcrypt.
    
    Args:
        password: Mot de passe en clair
        
    Returns:
        Mot de passe hashé
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT.
    
    Args:
        data: Données à encoder dans le token (ex: {"sub": user_id})
        expires_delta: Durée de validité du token
        
    Returns:
        Token JWT
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Décode un token JWT.
    
    Args:
        token: Token JWT à décoder
        
    Returns:
        Dict des données décodées ou None si erreur
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
