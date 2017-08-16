from distutils.core import setup

setup(
    name='batterytester',
    version='1.0',
    packages=['batterytester', 'batterytester.database',
              'batterytester.mylogger', 'batterytester.connector',
              'batterytester.main_test', 'batterytester.incoming_parser'],
    url='',
    license='',
    author='Sander Teunissen',
    author_email='s.teunissen@gmail.com',
    description=''
)
