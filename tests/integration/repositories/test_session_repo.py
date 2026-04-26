import uuid
from datetime import UTC, datetime, timedelta

import pytest

from domain.entities.session import Session
from domain.exceptions.session import SessionNotFoundError
from infrastructure.repositories.session_repo import SqlSessionRepository


def make_session(user_id: int, *, expired: bool = False, revoked: bool = False) -> Session:
    return Session(
        user_id=user_id,
        refresh_token_hash=f"token_{uuid.uuid4().hex}",
        expires_at=datetime.now(UTC) - timedelta(hours=1) if expired else datetime.now(UTC) + timedelta(days=1),
        is_revoked=revoked,
    )


async def test_save_assigns_id(db_session, saved_user):
    repo = SqlSessionRepository(db_session)

    saved = await repo.save(make_session(saved_user.id))

    assert saved.id is not None


async def test_get_by_id_found(db_session, saved_user):
    repo = SqlSessionRepository(db_session)
    session = await repo.save(make_session(saved_user.id))

    found = await repo.get_by_id(session.id)

    assert found is not None
    assert found.id == session.id


async def test_get_by_id_or_raise_not_found(db_session):
    repo = SqlSessionRepository(db_session)

    with pytest.raises(SessionNotFoundError):
        await repo.get_by_id_or_raise(uuid.uuid4())


async def test_delete_removes_session(db_session, saved_user):
    repo = SqlSessionRepository(db_session)
    session = await repo.save(make_session(saved_user.id))

    await repo.delete(session)

    assert await repo.get_by_id(session.id) is None


async def test_get_all_by_user_id(db_session, saved_user):
    repo = SqlSessionRepository(db_session)
    await repo.save(make_session(saved_user.id))
    await repo.save(make_session(saved_user.id))

    sessions = await repo.get_all_by_user_id(saved_user.id)

    assert len(sessions) == 2


async def test_delete_all_by_user_id(db_session, saved_user):
    repo = SqlSessionRepository(db_session)
    await repo.save(make_session(saved_user.id))
    await repo.save(make_session(saved_user.id))

    await repo.delete_all_by_user_id(saved_user.id)

    assert await repo.get_all_by_user_id(saved_user.id) == []


async def test_delete_invalid_removes_expired_and_revoked(db_session, saved_user):
    repo = SqlSessionRepository(db_session)
    valid = await repo.save(make_session(saved_user.id))
    expired = await repo.save(make_session(saved_user.id, expired=True))
    revoked = await repo.save(make_session(saved_user.id, revoked=True))

    await repo.delete_invalid_by_user_id(saved_user.id)

    remaining_ids = {s.id for s in await repo.get_all_by_user_id(saved_user.id)}
    assert valid.id in remaining_ids
    assert expired.id not in remaining_ids
    assert revoked.id not in remaining_ids


async def test_delete_others_keeps_excluded_session(db_session, saved_user):
    repo = SqlSessionRepository(db_session)
    keep = await repo.save(make_session(saved_user.id))
    await repo.save(make_session(saved_user.id))
    await repo.save(make_session(saved_user.id))

    await repo.delete_others_by_user_id(saved_user.id, exclude_session_id=keep.id)

    remaining = await repo.get_all_by_user_id(saved_user.id)
    assert len(remaining) == 1
    assert remaining[0].id == keep.id
