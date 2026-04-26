from datetime import UTC, datetime

from domain.entities.base import Email, UserRelatedHandle
from domain.entities.user import Role, User
from infrastructure.repositories.user_repo import SqlUserRepository


def make_user(n: int = 1) -> User:
    return User(
        email=Email(f"user{n}@test.com"),
        username=UserRelatedHandle(f"username{n}x"),
        password_hash="hashed",
        registered_at=datetime.now(UTC),
    )


async def test_save_assigns_id(db_session):
    repo = SqlUserRepository(db_session)

    saved = await repo.save(make_user())

    assert saved.id is not None


async def test_save_upserts(db_session):
    repo = SqlUserRepository(db_session)
    user = await repo.save(make_user())

    user.is_active = True
    updated = await repo.save(user)

    assert updated.id == user.id
    assert updated.is_active is True


async def test_save_preserves_roles(db_session):
    repo = SqlUserRepository(db_session)
    user = make_user()
    user.roles = {Role.ADMIN}

    saved = await repo.save(user)

    assert Role.ADMIN in saved.roles


async def test_get_by_username_found(db_session):
    repo = SqlUserRepository(db_session)
    user = await repo.save(make_user(2))

    found = await repo.get_by_username(user.username)

    assert found is not None
    assert found.id == user.id


async def test_get_by_username_not_found(db_session):
    repo = SqlUserRepository(db_session)

    found = await repo.get_by_username(UserRelatedHandle("unknownAbc"))

    assert found is None


async def test_get_by_email_found(db_session):
    repo = SqlUserRepository(db_session)
    user = await repo.save(make_user(3))

    found = await repo.get_by_email(user.email)

    assert found is not None
    assert found.id == user.id


async def test_get_by_id_found(db_session):
    repo = SqlUserRepository(db_session)
    user = await repo.save(make_user(4))

    found = await repo.get_by_id(user.id)

    assert found is not None
    assert found.username == user.username


async def test_get_by_id_not_found(db_session):
    repo = SqlUserRepository(db_session)

    found = await repo.get_by_id(999_999)

    assert found is None


async def test_get_all_returns_saved_users(db_session):
    repo = SqlUserRepository(db_session)
    await repo.save(make_user(5))
    await repo.save(make_user(6))

    all_users = await repo.get_all()

    assert len(all_users) >= 2
