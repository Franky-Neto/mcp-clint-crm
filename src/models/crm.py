from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Tag(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = ""
    name: str = ""
    color: str = ""


class User(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = ""
    first_name: str = ""
    last_name: str = ""
    email: str = ""


class Group(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = ""
    name: str = ""
    archived_at: str | None = None


class LostStatus(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = ""
    name: str = ""


class Stage(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = ""
    label: str = ""
    type: str = ""
    order: int = 0


class Origin(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = ""
    name: str = ""
    archived_at: str | None = None
    group: Group | None = None
    stages: list[Stage] = []


class Organization(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = ""
    name: str | None = ""
    custom_fields: dict | None = None
