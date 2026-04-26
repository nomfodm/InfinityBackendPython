import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from domain.entities.session import Session
from infrastructure.database.models.base import Base


class SessionModel(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    refresh_token_str: Mapped[str]
    is_revoked: Mapped[bool] = mapped_column(default=False)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user_agent: Mapped[str | None]
    ip_address: Mapped[str | None]

    def to_domain(self) -> Session:
        return Session(
            id=self.id,
            user_id=self.user_id,
            refresh_token_hash=self.refresh_token_str,
            is_revoked=self.is_revoked,
            expires_at=self.expires_at,
            created_at=self.created_at,
            last_used_at=self.last_used_at,
            user_agent=self.user_agent,
            ip_address=self.ip_address,
        )

    @classmethod
    def from_domain(cls, s: Session) -> "SessionModel":
        return cls(
            id=s.id or uuid.uuid4(),
            user_id=s.user_id,
            refresh_token_str=s.refresh_token_hash,
            is_revoked=s.is_revoked,
            expires_at=s.expires_at,
            created_at=s.created_at,
            last_used_at=s.last_used_at,
            user_agent=s.user_agent,
            ip_address=s.ip_address,
        )
