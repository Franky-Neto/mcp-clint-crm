from __future__ import annotations

from typing import TypeVar, overload

import httpx
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, TypeAdapter
from pydantic import ValidationError as PydanticValidationError

from models.common import ListResponse, PaginatedResult, SingleResponse

T = TypeVar("T", bound=BaseModel)


class ClintClient:
    BASE_URL = "https://api.clint.digital/v1"
    DEFAULT_LIMIT = 1000

    def __init__(self, api_key: str):
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "accept": "application/json",
                "api-token": api_key,
            },
            timeout=30.0,
        )

    # ── Error handling ──────────────────────────────────────────────

    @staticmethod
    def _extract_api_message(response: httpx.Response) -> str:
        """Extract a human-readable message from an API error response."""
        try:
            body = response.json()
            for key in ("message", "error", "detail"):
                if key in body:
                    return str(body[key])
        except (ValueError, KeyError, TypeError):
            pass
        return ""

    @staticmethod
    def _handle_http_error(exc: httpx.HTTPStatusError, path: str) -> ToolError:
        """Translate an HTTP error into a ToolError with a clear message."""
        status = exc.response.status_code
        api_msg = ClintClient._extract_api_message(exc.response)

        if status == 401:
            msg = "Authentication failed. The API key may be invalid or expired."
            if api_msg:
                msg += f" ({api_msg})"
        elif status == 404:
            msg = f"Resource not found: {path}"
        elif status == 422:
            msg = f"Validation error on {path}"
            if api_msg:
                msg += f": {api_msg}"
        elif status == 429:
            msg = "Rate limit exceeded. Please wait before retrying."
        elif 400 <= status < 500:
            msg = f"Client error ({status}) on {path}"
            if api_msg:
                msg += f": {api_msg}"
        else:
            msg = f"Clint API server error ({status}). Try again later."

        return ToolError(msg)

    # ── HTTP methods ────────────────────────────────────────────────

    @overload
    async def get(
        self, path: str, model: type[T], params: dict | None = None
    ) -> SingleResponse[T]: ...

    @overload
    async def get(
        self, path: str, model: None = None, params: dict | None = None
    ) -> dict: ...

    async def get(
        self, path: str, model: type[T] | None = None, params: dict | None = None
    ) -> SingleResponse[T] | dict:
        """GET request. If model is provided, parses {"data": {...}} into SingleResponse[T]."""
        try:
            response = await self._client.get(path, params=params)
            response.raise_for_status()
            raw = response.json()
            if model is not None:
                return SingleResponse[model](data=model.model_validate(raw["data"]))
            return raw
        except httpx.HTTPStatusError as exc:
            raise self._handle_http_error(exc, path) from exc
        except httpx.RequestError as exc:
            raise ToolError(
                f"Network error reaching Clint API ({type(exc).__name__}): {exc}"
            ) from exc
        except (KeyError, ValueError, PydanticValidationError) as exc:
            raise ToolError(
                f"Unexpected response format from {path}: {exc}"
            ) from exc

    async def get_list(
        self,
        path: str,
        model: type[T],
        params: dict | None = None,
        offset: int = 0,
    ) -> PaginatedResult[T]:
        """GET for list endpoints. Adds limit/offset and parses into PaginatedResult[T]."""
        try:
            params = dict(params) if params else {}
            params["limit"] = self.DEFAULT_LIMIT
            params["offset"] = offset
            response = await self._client.get(path, params=params)
            response.raise_for_status()
            raw = response.json()
            adapter = TypeAdapter(list[model])
            items = adapter.validate_python(raw["data"])
            list_resp = ListResponse[model](
                data=items, totalCount=raw.get("totalCount", len(items))
            )
            return PaginatedResult(response=list_resp, offset=offset)
        except httpx.HTTPStatusError as exc:
            raise self._handle_http_error(exc, path) from exc
        except httpx.RequestError as exc:
            raise ToolError(
                f"Network error reaching Clint API ({type(exc).__name__}): {exc}"
            ) from exc
        except (KeyError, ValueError, PydanticValidationError) as exc:
            raise ToolError(
                f"Unexpected response format from {path}: {exc}"
            ) from exc

    @overload
    async def post(
        self, path: str, model: type[T], data: dict | list | None = None
    ) -> SingleResponse[T]: ...

    @overload
    async def post(
        self, path: str, model: None = None, data: dict | list | None = None
    ) -> dict: ...

    async def post(
        self, path: str, model: type[T] | None = None, data: dict | list | None = None
    ) -> SingleResponse[T] | dict:
        """POST request. If model is provided, parses {"data": {...}} into SingleResponse[T]."""
        try:
            response = await self._client.post(path, json=data)
            response.raise_for_status()
            if response.status_code == 204 or not response.content:
                return {}
            raw = response.json()
            if model is not None:
                return SingleResponse[model](data=model.model_validate(raw["data"]))
            return raw
        except httpx.HTTPStatusError as exc:
            raise self._handle_http_error(exc, path) from exc
        except httpx.RequestError as exc:
            raise ToolError(
                f"Network error reaching Clint API ({type(exc).__name__}): {exc}"
            ) from exc
        except (KeyError, ValueError, PydanticValidationError) as exc:
            raise ToolError(
                f"Unexpected response format from {path}: {exc}"
            ) from exc

    async def delete(self, path: str, data: dict | None = None) -> dict:
        """DELETE, optionally with JSON body (e.g. remove_tags)."""
        try:
            if data is not None:
                response = await self._client.request("DELETE", path, json=data)
            else:
                response = await self._client.delete(path)
            response.raise_for_status()
            if response.status_code == 204 or not response.content:
                return {}
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise self._handle_http_error(exc, path) from exc
        except httpx.RequestError as exc:
            raise ToolError(
                f"Network error reaching Clint API ({type(exc).__name__}): {exc}"
            ) from exc
        except ValueError as exc:
            raise ToolError(
                f"Unexpected response format from {path}: {exc}"
            ) from exc

    async def close(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
