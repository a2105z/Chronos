from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import getSettings

pwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def hashPassword(password: str) -> str:
    return pwdContext.hash(password)


def verifyPassword(plain: str, hashed: str) -> bool:
    return pwdContext.verify(plain, hashed)


def createAccessToken(subject: Union[str, int], expiresMinutes: Optional[int] = None) -> str:
    settings = getSettings()
    expireDelta = expiresMinutes if expiresMinutes is not None else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=expireDelta)
    payload: dict[str, Any] = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decodeAccessToken(token: str) -> Optional[str]:
    settings = getSettings()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            return None
        return str(sub)
    except JWTError:
        return None
