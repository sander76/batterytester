import pytest

from batterytester.components.sensor.incoming_parser import get_measurement
from batterytester.core.atom import BooleanReferenceAtom


@pytest.fixture
def fake_bool_atom():
    async def fake_command():
        pass

    bool_atom = BooleanReferenceAtom(
        name='fake', command=fake_command, duration=1,
        reference={'7': True})
    return bool_atom


def test_reference_compare_pass(fake_bool_atom):
    _measurement = get_measurement('7', True)
    fake_bool_atom.sensor_data.append(_measurement)
    _atom_result = fake_bool_atom.reference_compare()
    assert _atom_result.passed.value is True


def test_reference_compare_fail(fake_bool_atom):
    _measurement = get_measurement('7', False)
    fake_bool_atom.sensor_data.append(_measurement)
    _atom_result = fake_bool_atom.reference_compare()
    assert _atom_result.passed.value is False


def test_reference_compare_fail_no_key(fake_bool_atom):
    _measurement = get_measurement('6', True)
    fake_bool_atom.sensor_data.append(_measurement)
    _atom_result = fake_bool_atom.reference_compare()
    assert _atom_result.passed.value is False
