from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from domain.exceptions.auth import (
    AccessDeniedError,
    EmailTakenError,
    InvalidCredentialError,
    UnauthenticatedError,
    UserBannedError,
    UsernameTakenError,
    UserNeedsActivationError,
)
from domain.exceptions.base import ValidationError
from domain.exceptions.launcher import LauncherReleaseNotFoundError
from domain.exceptions.minecraft import (
    InvalidMCAccessToken,
    InvalidMCServerID,
    MinecraftProfileNotFoundError,
    MinecraftSessionNotFoundError,
)
from domain.exceptions.session import (
    CannotRevokeSessionError,
    InvalidTokenError,
    SessionExpiredError,
    SessionNotFoundError,
    SessionRevokedError,
    TokenAuthenticityError,
)
from domain.exceptions.user import InvalidVerificationCode, NicknameTakenError, UserNotFoundError
from domain.exceptions.wardrobe import (
    CannotPublishAddedTextureError,
    TextureCatalogItemNotFoundError,
    WardrobeItemNotFoundError,
)


def register_exception_handlers(app: FastAPI) -> None:
    handlers = {
        # 401
        UnauthenticatedError: 401,
        InvalidCredentialError: 401,
        InvalidTokenError: 401,
        TokenAuthenticityError: 401,
        SessionExpiredError: 401,
        SessionRevokedError: 401,
        InvalidMCAccessToken: 401,
        # 403
        AccessDeniedError: 403,
        UserBannedError: 403,
        UserNeedsActivationError: 403,
        CannotRevokeSessionError: 403,
        CannotPublishAddedTextureError: 403,
        # 404
        UserNotFoundError: 404,
        SessionNotFoundError: 404,
        MinecraftSessionNotFoundError: 404,
        MinecraftProfileNotFoundError: 404,
        WardrobeItemNotFoundError: 404,
        TextureCatalogItemNotFoundError: 404,
        LauncherReleaseNotFoundError: 404,
        # 409
        EmailTakenError: 409,
        UsernameTakenError: 409,
        NicknameTakenError: 409,
        # 422
        ValidationError: 422,
        InvalidVerificationCode: 422,
        InvalidMCServerID: 422,
    }

    for exc_class, status_code in handlers.items():

        def make_handler(code: int):
            async def handler(request: Request, exc: Exception) -> JSONResponse:
                return JSONResponse(status_code=code, content={"detail": str(exc), "code": type(exc).__name__})

            return handler

        app.add_exception_handler(exc_class, make_handler(status_code))
