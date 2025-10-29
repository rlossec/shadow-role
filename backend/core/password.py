from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def get_password_hash(password: str) -> str:
    """Hash a password using the recommended algorithm"""
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return password_hash.verify(plain_password, hashed_password)

