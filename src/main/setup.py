#!/usr/bin/env python

import setuptools

with open("../../README.md", "r") as fh:
	ld = fh.read()

setup(name = 'PyAutoMan',
	versio n= '0.1.0.dev',
	description = 'Python bindings for AutoMan Runtime (in Scala)',
	author = 'Kevin Feveck',
	packages = setuptools.find_packages(),
	license = "GNU GPLv2",
	description = "A small example package",
	keywords = 'automan crowdsource quality-assurance'
	long_description = ld,
	long_description_content_type="text/markdown",
	python_requires='>=2.7, !=3.0.*, !=3.1.*, <3.5.*',
	package_data = {
		'' :['*.md'],
		''
	},
	classifiers=(
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3.2",
		"Programming Language :: Python :: 3.3",
		"Programming Language :: Python :: 3.4",
		"Programming Language :: Python :: 3.5",
		"License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
		"Operating System :: OS Independent",
	),
 )

