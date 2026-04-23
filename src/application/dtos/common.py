from dataclasses import dataclass


@dataclass(frozen=True)
class StatusResponse:
    ok: bool = True
