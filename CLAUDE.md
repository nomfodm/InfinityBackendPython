# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/unit/application/use_cases/auth/test_login.py

# Run a single test by name
uv run pytest -k test_login_success

# Run tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Lint
uv run ruff check .

# Format
uv run ruff format .
```

## Architecture

Clean Architecture with strict inward dependencies: `infrastructure` → `application` → `domain`.

```
src/
├── domain/          # No external dependencies
│   ├── entities/    # Entities (mutable dataclasses) + value objects (frozen + validation)
│   ├── exceptions/  # All inherit from DomainError
│   └── interfaces/  # Protocols for repositories, UoW, and services
├── application/
│   ├── use_cases/   # One file per feature, grouped by domain
│   ├── services/    # AuthService — orchestrates tokens and session creation
│   ├── dtos/        # Frozen dataclasses for inputs; response DTOs with .from_domain()
│   ├── decorators/  # @require_login — checks active, not banned
│   └── constants.py # TTLs and token expiry values
└── infrastructure/  # Concrete implementations of domain Protocols
```

## Domain Layer Conventions

**Value objects** live in `domain/entities/base.py` — frozen dataclasses that validate in `__post_init__` and raise `ValidationError`. Examples: `Email`, `UserRelatedHandle`, `ContentLabel`.

**Entities** are plain mutable dataclasses with `id: T | None = None` (set by persistence). Never frozen.

**Enums** extend `StrEnum`.

**Repositories** are Protocols in `domain/interfaces/repositories/`. Each repo defines both nullable (`get_by_x`) and raising (`get_by_x_or_raise`) variants. New exceptions go in `domain/exceptions/{domain}.py`, inheriting from `DomainError`.

## Use Case Pattern

Every use case follows this exact structure:

```python
@dataclass(frozen=True)
class DoSomethingRequest:
    field: Type

class DoSomethingUseCase:
    def __init__(self, *, uow: UnitOfWork, service: SomeService):
        self._uow = uow
        self._service = service

    async def execute(self, *, dto: DoSomethingRequest) -> SomeResponse:
        async with self._uow:
            # repository access via self._uow.{repo}
            await self._uow.commit()
            return SomeResponse(...)
```

All constructor args are keyword-only (`*,`). The UoW is always used as an async context manager. `commit()` is only called for write operations.

## Unit of Work

`UnitOfWork` (Protocol in `domain/interfaces/unit_of_work.py`) exposes all repositories as attributes: `users`, `sessions`, `verification_codes`, `minecraft_profiles`, `minecraft_sessions`, `wardrobe`, `textures`, `texture_catalog`.

## Testing Conventions

Global fixtures in `tests/conftest.py`: `mock_uow`, `fake_user`, `active_user`, `fake_session`. The `mock_uow` is a `MagicMock` pre-configured as an async context manager with all repo attributes as `AsyncMock`.

Per-domain fixtures in `tests/unit/.../conftest.py` — e.g. `mock_auth_service` for auth use cases.

Typical test structure: set up mock return values → call `use_case.execute(dto=dto)` → assert on result and mock call assertions (`assert_awaited_once_with`, `assert_not_called`).

Use `if x is None:` not `if not x:` when checking for None — value objects are truthy even when logically "empty".
