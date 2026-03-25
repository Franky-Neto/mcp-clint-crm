from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class FieldOption(BaseModel):
    model_config = ConfigDict(extra="allow")

    label: str = ""


class FieldDefinition(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str = "TEXT"
    label: str = ""
    group: str = "default"
    options: list[FieldOption] = []


class AccountFields(BaseModel):
    model_config = ConfigDict(extra="allow")

    groups: dict[str, dict[str, str]] = {}
    fields: dict[str, dict[str, FieldDefinition]] = {}
