from datetime import UTC, datetime, timedelta

from domain.entities.login_history import LoginHistoryEntry
from infrastructure.repositories.login_history_repo import SqlLoginHistoryRepository


def make_entry(user_id: int, *, minutes_ago: int = 0) -> LoginHistoryEntry:
    return LoginHistoryEntry(
        user_id=user_id,
        timestamp=datetime.now(UTC) - timedelta(minutes=minutes_ago),
        ip_address="127.0.0.1",
        user_agent="TestAgent/1.0",
    )


async def test_save_does_not_return_value(db_session, saved_user):
    repo = SqlLoginHistoryRepository(db_session)

    result = await repo.save(make_entry(saved_user.id))

    assert result is None


async def test_get_by_user_id_returns_all_entries(db_session, saved_user):
    repo = SqlLoginHistoryRepository(db_session)
    await repo.save(make_entry(saved_user.id, minutes_ago=10))
    await repo.save(make_entry(saved_user.id, minutes_ago=5))
    await repo.save(make_entry(saved_user.id, minutes_ago=0))

    entries = await repo.get_by_user_id(saved_user.id)

    assert len(entries) == 3


async def test_get_by_user_id_ordered_newest_first(db_session, saved_user):
    repo = SqlLoginHistoryRepository(db_session)
    await repo.save(make_entry(saved_user.id, minutes_ago=30))
    await repo.save(make_entry(saved_user.id, minutes_ago=10))
    await repo.save(make_entry(saved_user.id, minutes_ago=1))

    entries = await repo.get_by_user_id(saved_user.id)

    timestamps = [e.timestamp for e in entries]
    assert timestamps == sorted(timestamps, reverse=True)


async def test_get_by_user_id_empty_for_unknown_user(db_session):
    repo = SqlLoginHistoryRepository(db_session)

    entries = await repo.get_by_user_id(999_999)

    assert entries == []


async def test_save_preserves_ip_and_user_agent(db_session, saved_user):
    repo = SqlLoginHistoryRepository(db_session)
    await repo.save(
        LoginHistoryEntry(
            user_id=saved_user.id,
            timestamp=datetime.now(UTC),
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )
    )

    entries = await repo.get_by_user_id(saved_user.id)

    assert entries[0].ip_address == "192.168.1.1"
    assert entries[0].user_agent == "Mozilla/5.0"
