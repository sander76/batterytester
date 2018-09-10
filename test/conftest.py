from unittest.mock import MagicMock, Mock

import pytest

from batterytester.components.datahandlers.influx import Influx
from batterytester.components.datahandlers.messaging import Messaging
from batterytester.core.base_test import BaseTest
from batterytester.core.helpers.message_data import (
    Data,
    TYPE_TIME,
    TestWarmup,
    TestFatal,
)
from test.fake_components import (
    FakeBaseTest,
    FakeVoltsAmpsSensor,
    FakeActor,
    AsyncMock,
)


@pytest.fixture
def fake_time_stamp():
    ts = Data(123456789, type_=TYPE_TIME)
    return ts


@pytest.fixture
def base_test():
    base_test = BaseTest(test_name="test", loop_count=1)
    base_test.bus.notify = Mock()
    return base_test


@pytest.fixture
def fake_test():
    fake_test = FakeBaseTest(test_name="fake_test", loop_count=1)
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
def fake_messaging():
    fake_ms = Messaging()

    return fake_ms


@pytest.fixture
def fake_influx():
    _influx = Influx(host="127.0.0.1", buffer_size=5)
    _influx._send = AsyncMock()
    _influx.test_name = "fake_test"
    _influx.measurement = "fake_test"

    return _influx


@pytest.fixture
def fake_influx_nobus(fake_influx):
    fake_influx.bus = MagicMock()
    fake_influx.bus.add_async_task = Mock()

    return fake_influx


@pytest.fixture
def test_warmup_data(fake_time_stamp):
    warmup = TestWarmup("test_test", 1)
    warmup.started = fake_time_stamp
    return warmup


@pytest.fixture
def fatal_data(fake_time_stamp):
    ft = TestFatal("fatal reason unknown.")
    ft.time = fake_time_stamp
    ft.time_finished = fake_time_stamp
    return ft
