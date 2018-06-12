from unittest.mock import Mock

import pytest
from aiopvapi.hub import Version

from batterytester.components.actors.powerview_version_checker import \
    PowerViewVersionChecker


@pytest.fixture
def version1():
    version = Version(123, 456, 789)
    return version


@pytest.fixture
def checker(version1):
    checker = PowerViewVersionChecker(hub_ip='123.123.123.123')
    checker.hub = Mock(main_processor_version=version1,
                       radio_version=version1)
    # checker.hub._main_processor_version = version1
    # checker.hub._radio_version = version1
    return checker


@pytest.fixture
def version2():
    version = Version(234, 567, 890)
    return version


def test_check_version(checker, version2):
    _ref_ver = checker._make_response()
    _ver = checker._check_version()
    assert _ref_ver == _ver

    _ver = checker._check_version()
    assert _ver is None

    checker.hub.main_processor_version = version2
    checker.hub.radio_version = version2
    _ref_ver = checker._make_response(include_old=True)
    _ver = checker._check_version()
    assert _ref_ver == _ver
