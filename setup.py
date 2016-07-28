#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    # TODO: put package requirements here
    'pip==8.1.2',
    'bumpversion==0.5.3',
    'wheel==0.29.0',
    'watchdog==0.8.3',
    'flake8==2.6.0',
    'tox==2.3.1',
    'coverage==4.1',
    'Sphinx==1.4.4',
    'cryptography>=1.4', # Problem here, need libssl-dev
    'cffi', # Problem here, need ligffi-dev
    'PyYAML',
    'enum34==1.1.6',
    'id3reader==1.53.20070415',
    'idna==2.1',
    'ipaddress==1.0.16',
    'ndg-httpsclient==0.4.0',
    'mutagen==1.31',
    'pyasn1==0.1.9',
    'pycparser==2.14',
    'pyOpenSSL',
    'pymongo==3.2.2',
    'requests[security]',
    'six>=1.10.0',
    'Twisted>=16.2.0',
    'zope.interface>=4.1.3',
    'python-vlc',
    'pyacoustid',
    'musicbrainzngs',
    'service_identity',
    'pytaglib>=1.2.1'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='nukebox2000',
    version='0.1.1',
    description="Network jukebox",
    long_description=readme + '\n\n' + history,
    author="Darren Dowdall",
    author_email='darr3n.dowdall@gmail.com',
    url='https://github.com/k1nk33/nukebox2000',
    packages=[
        'nukebox2000',
    ],
    package_dir={'nukebox2000':
                 'nukebox2000'},
    entry_points={
        'console_scripts': [
            'nukebox2000=nukebox2000.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='nukebox2000',
    classifiers=[
        'Development Status :: 3 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        #"Programming Language :: Python :: 2",
        #'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        #'Programming Language :: Python :: 3',
        #'Programming Language :: Python :: 3.3',
        #'Programming Language :: Python :: 3.4',
        #'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
