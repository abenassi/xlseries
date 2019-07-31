#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup
import os

with open(os.path.abspath('README.md')) as readme_file:
    readme = readme_file.read()

with open(os.path.abspath("requirements.txt")) as f:
    requirements = [req.strip() for req in f.readlines()]

with open(os.path.abspath("requirements_dev.txt")) as f:
    test_requirements = [req.strip() for req in f.readlines()]

with open('PYPI_LONG_DESCRIPTION.rst') as readme_file:
    readme = readme_file.read()


setup(
    name='xlseries',
    version='0.2.2',
    description="Python package to scrape time series data from excel files.",
    long_description=readme,
    author="Agustin Benassi",
    author_email='agusbenassi@gmail.com',
    maintainer="Agustin Benassi",
    maintainer_email='agusbenassi@gmail.com',
    url='https://github.com/abenassi/xlseries',
    download_url='https://github.com/abenassi/xlseries/archive/master.zip',
    packages=[
        'xlseries',
        'xlseries.strategies',
        'xlseries.strategies.clean',
        'xlseries.strategies.discover',
        'xlseries.strategies.get',
        'xlseries.utils'
    ],
    package_dir={'xlseries': 'xlseries'},
    include_package_data=True,
    install_requires=requirements,
    license="GPLv3+",
    zip_safe=False,
    keywords="xlseries excel time series data opendata scraper",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Office/Business'
    ],
    test_suite='nose.collector',
    tests_require=test_requirements
)
