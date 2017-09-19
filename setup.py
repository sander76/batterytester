from distutils.core import setup
from setuptools import find_packages
setup(
    name='batterytester',
    version='1.2.1',
    # packages=['batterytester', 'batterytester.database',
    #           'batterytester.mylogger', 'batterytester.connector',
    #           'batterytester.main_test', 'batterytester.incoming_parser',
    #           'batterytester.test_atom'],
    packages = find_packages(),
    url='',
    license='',
    author='Sander Teunissen',
    author_email='s.teunissen@gmail.com',
    description=''
)
