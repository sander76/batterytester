from setuptools import setup, find_packages

setup(
    name='batterytester',
    version='1.2.8',
    packages=find_packages(exclude='test'),
    url='',
    license='',
    author='Sander Teunissen',
    author_email='s.teunissen@gmail.com',
    description='',
    install_requires=['pyserial', 'aiopvapi', 'aiohttp', 'python-slugify']
)
