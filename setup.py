#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('multiweather/version.py', encoding='utf-8') as f:
    exec(f.read())

setup(
    name="multiweather",
    description="Python weather library with multiple backends",
    version=__version__,
    url="https://github.com/jlu5/multiweather",

    author="James Lu",
    author_email="james@overdrivenetworks.com",

    license="MIT/Expat",
    classifiers=[
        # https://pypi.org/classifiers/
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],

    packages=find_packages(exclude=['tests']),
)
