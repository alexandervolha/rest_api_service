import asyncio

import pytest
from asynctest import CoroutineMock

from rest_api_service.utils import async_retry


pytestmark = pytest.mark.asyncio


class CustomException(Exception):
    pass


async def test_async_retry_success():
    coromock = CoroutineMock(side_effect=[CustomException, 'data'])
    result = await async_retry(retry_cooldown=0)(coromock)()
    assert result == 'data'


async def test_async_retry_custom_error():
    coromock = CoroutineMock(side_effect=CustomException)
    with pytest.raises(CustomException):
        await async_retry(max_tries=2, retry_cooldown=0)(coromock)()


async def test_async_retry_cancelled_error():
    coromock = CoroutineMock(side_effect=CustomException)
    fut = asyncio.ensure_future(async_retry(retry_cooldown=0)(coromock)())
    fut.cancel()
    with pytest.raises(asyncio.CancelledError):
        await fut
