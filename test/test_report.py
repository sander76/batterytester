import os

from batterytester.core.datahandlers.report import create_output_location


def test_output_folder():
    _current_folder = os.getcwd()
    full_path = create_output_location('abc', 'report')
    pass