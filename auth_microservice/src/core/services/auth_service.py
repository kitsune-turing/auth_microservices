"""Core authentication service implementing business logic.

This service is framework-agnostic and only depends on repository ports.
It is intended to be used from adapters (HTTP controllers, CLI, etc.).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4
import jwt

from zoneinfo import ZoneInfo

from src.core.config import config
from src.core.domain.entity import AuthToken, TokenType


class AuthService:
    """Small domain service to handle token creation and revocation.

    The service deliberately does not perform user credential verification.
    That responsibility must live in a separate adapter (UserAuthenticator)
    and be injected by the caller. This keeps this service testable and
    focused on token/session management (hexagonal boundary).
    """

    def __init__(self, auth_token_repo, session_repo=None):
        self.auth_token_repo = auth_token_repo
        self.session_repo = session_repo

    def _now_utc(self) -> datetime:
        return datetime.now(timezone.utc)

    def _tz_colombia(self) -> ZoneInfo:
        return ZoneInfo("America/Bogota")

    def _format_dt_colombia(self, dt: datetime) -> str:
        return dt.astimezone(self._tz_colombia()).strftime("%d/%m/%Y %H:%M:%S")

    def _create_jwt(self, user_id: UUID, token_type: TokenType, expires_delta: timedelta) -> tuple[str, datetime]:
        now = self._now_utc()
        exp = now + expires_delta
        payload = {
            "sub": str(user_id),
            "type": token_type.value,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
        }
        token = jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
        return token, exp

    async def create_tokens_for_user(self, user_id: UUID) -> dict:
        """Create access and refresh tokens for a user and persist them.

        Returns a dictionary with token strings and expiry metadata.
        """
        # Create refresh token
        refresh_delta = timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
        access_delta = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

        refresh_token_str, refresh_exp = self._create_jwt(user_id, TokenType.REFRESH, refresh_delta)
        access_token_str, access_exp = self._create_jwt(user_id, TokenType.ACCESS, access_delta)

        # Persist tokens using repository (if provided)
        now = self._now_utc()

        refresh_entity = AuthToken(
            user_id=user_id,
            token_type=TokenType.REFRESH,
            token_string=refresh_token_str,
            expires_at=refresh_exp,
        )

        access_entity = AuthToken(
            user_id=user_id,
            token_type=TokenType.ACCESS,
            token_string=access_token_str,
            expires_at=access_exp,
        )

        # Save tokens if repository is async-compatible
        if hasattr(self.auth_token_repo, "save"):
            # support both sync and async repos
            maybe_save = self.auth_token_repo.save
            if callable(maybe_save):
                saved_refresh = maybe_save(refresh_entity)
                saved_access = maybe_save(access_entity)
                # If coroutines were returned (async repo) await them
                if hasattr(saved_refresh, "__await__"):
                    saved_refresh = await saved_refresh
                    saved_access = await saved_access

        return {
            "refresh": refresh_token_str,
            "access": access_token_str,
            "token_expiry": self._format_dt_colombia(access_exp),
            "current_time": self._format_dt_colombia(now),
        }

    async def revoke_user_tokens(self, user_id: UUID) -> int:
        """Revoke all non-revoked tokens for a user. Returns number revoked."""
        if not hasattr(self.auth_token_repo, "revoke_all_user_tokens"):
            raise RuntimeError("AuthToken repository does not implement revoke_all_user_tokens")

        maybe = self.auth_token_repo.revoke_all_user_tokens(user_id)
        if hasattr(maybe, "__await__"):
            return await maybe
        return maybe
