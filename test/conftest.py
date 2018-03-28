from unittest.mock import MagicMock

import pytest

from batterytester.core.datahandlers.influx import Influx
from batterytester.core.datahandlers.messaging import Messaging
from test.fake_components import FakeBaseTest, FakeVoltsAmpsSensor, FakeActor


def AsyncMock(*args, **kwargs):
    m = MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro


@pytest.fixture
def fake_test():
    fake_test = FakeBaseTest(test_name='fake_test', loop_count=1)
    return fake_test


@pytest.fixture
def fake_actor():
    fake_actor = FakeActor()
    return fake_actor


@pytest.fixture
def fake_sensor():
    sensor = FakeVoltsAmpsSensor()
    return sensor


@pytest.fixture
def fake_influx():
    influx = Influx('127.0.0.1', buffer_size=5)
    influx._send = AsyncMock()
    return influx

@pytest.fixture
def fake_messaging():
    fake_ms = Messaging()
    return fake_ms

