#!/usr/bin/env python

from setuptools import setup, find_packages
from os import path

with open("README.md", "r") as fh:
	ld = fh.read()

setup(name = 'automanpy',
	version= '0.4.1.b0',
	description = 'Python bindings for AutoMan Runtime. Software is current in development, and not properly tested.',
	author = 'Kevin Feveck',
	url="https://github.com/kevfev/AutomanPy/",
	packages = find_packages(),
	license = "GNU GPLv2",
	keywords = 'automan crowdsource quality-assurance',
	long_description = ld,
	long_description_content_type="text/markdown",
	include_package_data=True,
	python_requires = '>=2.7.15, !=3.0.*, !=3.1.*, <3.5.*',
	install_requires = ['googleapis-common-protos>=1.5.3',
						'grpcio>=1.13.0',
						'grpcio-tools>=1.13.0'],
	classifiers=(
		"Development Status :: 3 - Alpha",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3.2",
		"Programming Language :: Python :: 3.3",
		"Programming Language :: Python :: 3.4",
		"Programming Language :: Python :: 3.5",
		"License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
		"Operating System :: OS Independent",
	),
 )

