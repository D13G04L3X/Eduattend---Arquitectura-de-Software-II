# src/user_service/infrastructure/adapters/outbound/postgres_user_repository.py
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column

from ....domain.exception.user_exceptions import DuplicateEmailError
from ....domain.model.user import User
from ....domain.model.user_profile import UserProfile
from ....domain.service.user_domain_service import IUserRepository
from ...config.db_config import Base
from ...mappers.user_mapper import profile_from_orm, user_from_orm


class UserOrmModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class UserProfileOrmModel(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    bio: Mapped[str | None] = mapped_column(String(500), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)


class PostgresUserRepository(IUserRepository):
    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def find_by_id(self, user_id: str) -> User | None:
        session = self._session_factory()
        try:
            model = session.get(UserOrmModel, user_id)
            if model is None:
                return None
            return user_from_orm(model)
        finally:
            session.close()

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

    def list_all_users(self) -> list[User]:
        session = self._session_factory()
        try:
            statement = select(UserOrmModel).order_by(UserOrmModel.created_at.desc())
            rows = session.execute(statement).scalars().all()
            return [user_from_orm(row) for row in rows]
        finally:
            session.close()

    def save_user(self, user: User) -> User:
        session = self._session_factory()
        try:
            model = session.get(UserOrmModel, user.id)
            if model is None:
                model = UserOrmModel(
                    id=user.id,
                    email=user.email,
                    full_name=user.full_name,
                    role=user.role.value,
                    created_at=datetime.now(UTC).replace(tzinfo=None),
                )
                session.add(model)
            else:
                model.email = user.email
                model.full_name = user.full_name
                model.role = user.role.value

            session.commit()
            session.refresh(model)
            return user_from_orm(model)
        except IntegrityError as exc:
            session.rollback()
            raise DuplicateEmailError(f"El email {user.email} ya esta registrado.") from exc
        finally:
            session.close()

    def get_profile(self, user_id: str) -> UserProfile | None:
        session = self._session_factory()
        try:
            model = session.get(UserProfileOrmModel, user_id)
            if model is None:
                return None
            return profile_from_orm(model)
        finally:
            session.close()

    def save_profile(self, profile: UserProfile) -> UserProfile:
        session = self._session_factory()
        try:
            model = session.get(UserProfileOrmModel, profile.user_id)
            if model is None:
                model = UserProfileOrmModel(
                    user_id=profile.user_id,
                    bio=profile.bio,
                    avatar_url=profile.avatar_url,
                    phone=profile.phone,
                )
                session.add(model)
            else:
                model.bio = profile.bio
                model.avatar_url = profile.avatar_url
                model.phone = profile.phone

            session.commit()
            session.refresh(model)
            return profile_from_orm(model)
        finally:
            session.close()
