from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Contact(BaseModel):
    model_config = ConfigDict(extra="allow")

    uuid: str = ""
    name: str = ""
    ddi: str | None = None
    phone: str | None = None
    email: str | None = None
    username: str | None = None
    instagram: dict | str | None = None
    fields: dict | None = None


class DealUser(BaseModel):
    model_config = ConfigDict(extra="allow")

    full_name: str = ""
    email: str = ""


class DealContact(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = ""
    phone: str | None = None
    email: str | None = None
    ddi: str | None = None
    instagram: dict | str | None = None


class Deal(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = ""
    status: str = ""
    stage: str | None = None
    value: float = 0.0
    contact: DealContact | None = None
    user: DealUser | None = None
    created_at: str | None = None
    updated_at: str | None = None
    won_at: str | None = None
    lost_at: str | None = None
    fields: dict | None = None
