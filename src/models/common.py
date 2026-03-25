from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ListResponse(BaseModel, Generic[T]):
    data: list[T]
    totalCount: int


class SingleResponse(BaseModel, Generic[T]):
    data: T


@dataclass
class PaginatedResult(Generic[T]):
    response: ListResponse[T]
    offset: int
