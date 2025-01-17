# See license.txt for license details.
# Copyright (c) 2016 onwards Chris Withers

import os

from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

optionals = ['sqlalchemy']

setup(
    name='chide',
    version='3.1.0',
    author='Chris Withers',
    author_email='chris@withers.org',
    license='MIT',
    description="Quickly create sample objects from data.",
    long_description=open(os.path.join(base_dir, 'README.rst')).read(),
    url='https://github.com/cjw296/chide',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.11",
    extras_require=dict(
        test=[
            'mypy',
            'pytest',
            'pytest-cov',
            'sybil',
            'testfixtures',
        ] + optionals,
        docs=[
            'furo',
            'sphinx',
        ] + optionals,
        release=[
            'twine',
            'wheel'
        ]
    ),
)
