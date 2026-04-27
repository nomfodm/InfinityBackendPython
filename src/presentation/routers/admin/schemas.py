import datetime

from pydantic import BaseModel

from application.use_cases.admin.ban_user import BanType


class BanUserRequest(BaseModel):
    ban_type: BanType
    banned_till: datetime.datetime | None = None
