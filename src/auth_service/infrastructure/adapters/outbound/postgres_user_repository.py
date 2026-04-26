# src/auth_service/infrastructure/adapters/outbound/postgres_user_repository.py
from datetime import datetime

from sqlalchemy import DateTime, String, select
from sqlalchemy.orm import Mapped, mapped_column

from ....domain.model.user import User
from ....domain.service.auth_service import IUserRepository
from ...config.db_config import Base
from ...mappers.user_mapper import user_from_orm


class UserOrmModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class PostgresUserRepository(IUserRepository):
    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def find_by_email(self, email: str) -> User | None:
        session = self._session_factory()
        try:
            statement = select(UserOrmModel).where(UserOrmModel.email == email)
            model = session.execute(statement).scalar_one_or_none()
            if model is None:
                return None
            return user_from_orm(model)
        finally:
            session.close()
