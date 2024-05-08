from functools import wraps
from typing import Any, Callable, TypeVar
from httpx import HTTPStatusError
from modules.subtitle_providers.i_provider import ISubtitleProvider

T = TypeVar("T", bound=ISubtitleProvider)


def auth_required(func: Callable[[T, Any], Any]) -> Callable[[T, Any], Any]:
    @wraps(func)
    async def wrapper(self: T, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except HTTPStatusError as e:
            if not self.is_authenticated(status_code=e.response.status_code):
                # Authentication failed or token expired
                self.token = None
                await self.login()
                return await func(self, *args, **kwargs)
            else:
                raise e

    return wrapper
