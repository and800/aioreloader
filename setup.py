from setuptools import setup
import re

with open('aioreloader.py', 'r') as module:
    content = module.read()
pattern = r"""^__version__\s*=\s*['"]([^'"]*)['"]"""
version = re.search(pattern, content, re.M).group(1)

with open('README.rst', 'r') as readme:
    long_description = readme.read()

setup(
    name='aioreloader',
    version=version,
    description='Port of tornado reloader to asyncio',
    long_description=long_description,
    url='https://github.com/and800/aioreloader',
    author='Andriy Maletsky',
    author_email='andriy.maletsky@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
    ],
    keywords='aiohttp asyncio',
    py_modules=['aioreloader'],
    extras_require={
        ':python_version=="3.3"': ['asyncio'],
    },
)
