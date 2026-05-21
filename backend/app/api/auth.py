from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from app.core.deps import CurrentUser, DbSession
from app.core.security import createAccessToken, hashPassword, verifyPassword
from app.models.user import User
from app.schemas.auth import TokenResponse, UserRead, UserRegister

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _authenticate(session: DbSession, email: str, password: str) -> User:
    user = session.exec(select(User).where(User.email == email.lower())).first()
    if user is None or not verifyPassword(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if user.id is None:
        raise HTTPException(status_code=500, detail="User missing id")
    return user


@router.post("/register", response_model=UserRead, status_code=201)
def register(body: UserRegister, session: DbSession) -> User:
    existing = session.exec(select(User).where(User.email == body.email.lower())).first()
    if existing is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=body.email.lower(),
        hashed_password=hashPassword(body.password),
        name=body.name.strip() or body.email.split("@")[0],
        created_at=datetime.utcnow()
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, session: DbSession) -> TokenResponse:
    """Accept JSON {email, password} or OAuth2 form (username=email, password)."""
    contentType = request.headers.get("content-type", "")
    email = ""
    password = ""

    if "application/json" in contentType:
        data = await request.json()
        email = str(data.get("email") or data.get("username") or "")
        password = str(data.get("password") or "")
    else:
        form = await request.form()
        email = str(form.get("username") or form.get("email") or "")
        password = str(form.get("password") or "")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="email/username and password are required"
        )

    user = _authenticate(session, email, password)
    return TokenResponse(access_token=createAccessToken(user.id))


@router.post("/token", response_model=TokenResponse, include_in_schema=False)
def loginToken(session: DbSession, formData: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    """OAuth2 password flow helper for Swagger Authorize."""
    user = _authenticate(session, formData.username, formData.password)
    return TokenResponse(access_token=createAccessToken(user.id))


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser) -> User:
    return user
