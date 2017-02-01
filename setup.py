from setuptools import setup

setup(
    name='aioreloader',
    version='0.0.0',
    description='Port of tornado reloader to asyncio',
    url='https://github.com/and800/aioreloader',
    author='Andriy Maletsky',
    author_email='andriy.maletsky@gmail.com',
    license='MIT',
    py_modules=['aioreloader'],
    extras_require={
        ':python_version=="3.3"': ['asyncio'],
    },
)
