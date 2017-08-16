from distutils.core import setup

setup(
    name='batterytester',
    version='1.1',
    packages=['batterytester', 'batterytester.database',
              'batterytester.mylogger', 'batterytester.connector',
              'batterytester.main_test', 'batterytester.incoming_parser',
              'batterytester.test_atom'],
    url='',
    license='',
    author='Sander Teunissen',
    author_email='s.teunissen@gmail.com',
    description=''
)
