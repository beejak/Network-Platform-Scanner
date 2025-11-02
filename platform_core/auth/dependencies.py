from typing import AsyncGenerator, Callable, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from platform_core.auth.models import User
from platform_core.auth.rbac import RBACManager
from platform_core.config import settings
from platform_core.database.postgres import DatabaseManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenData(BaseModel):  # type: ignore
    email: Optional[str] = None


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    db_manager = DatabaseManager(settings.DATABASE_URL)
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=400, detail="Tenant ID not found in request state"
        )
    session = await db_manager.get_session(tenant_id)
    try:
        yield session
    finally:
        await session.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    result = await db.execute(select(User).where(User.email == token_data.email))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user  # type: ignore


def permission_checker(resource: str, action: str) -> Callable[..., None]:
    async def check_permissions(
        current_user: User = Depends(get_current_user),
        rbac_manager: RBACManager = Depends(lambda: RBACManager(settings.DATABASE_URL)),
    ) -> None:
        if not await rbac_manager.check_permission(
            str(current_user.id), resource, action, str(current_user.tenant_id)
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have enough permissions",
            )

    return check_permissions  # type: ignore
