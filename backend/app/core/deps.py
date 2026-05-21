from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.core.security import decodeAccessToken
from app.db import getSession
from app.models.user import User

oauth2Scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def getCurrentUser(
    token: Annotated[str, Depends(oauth2Scheme)],
    session: Annotated[Session, Depends(getSession)]
) -> User:
    credentialsException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    subject = decodeAccessToken(token)
    if subject is None:
        raise credentialsException
    try:
        userId = int(subject)
    except ValueError as exc:
        raise credentialsException from exc

    user = session.get(User, userId)
    if user is None:
        raise credentialsException
    return user


def getOptionalUser(
    session: Annotated[Session, Depends(getSession)],
    token: Annotated[Optional[str], Depends(OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False))] = None
) -> Optional[User]:
    if not token:
        return None
    subject = decodeAccessToken(token)
    if subject is None:
        return None
    try:
        userId = int(subject)
    except ValueError:
        return None
    return session.get(User, userId)


CurrentUser = Annotated[User, Depends(getCurrentUser)]
DbSession = Annotated[Session, Depends(getSession)]
