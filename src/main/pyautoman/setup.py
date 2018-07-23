#!/usr/bin/env python

from setuptools import setup, find_packages

with open("../../../README.md", "r") as fh:
	ld = fh.read()

setup(name = 'pyautoman',
	version= '0.1.0.dev',
	description = 'Python bindings for AutoMan Runtime (in Scala)',
	author = 'Kevin Feveck',
	packages = find_packages(),
	license = "GNU GPLv2",
	keywords = 'automan crowdsource quality-assurance',
	long_description = ld,
	long_description_content_type="text/markdown",
	python_requires = '>=2.7, !=3.0.*, !=3.1.*, <3.5.*',
	install_requires = ['googleapis-common-protos>=1.5.3',
						'grpcio>=1.13.0',
						'grpcio-tools>=1.13.0'],
	package_data = {
		'' :['*.md'],
		'' :['*.txt'],
		'core/rpc_server/pack/lib' :['core/rpc_server/pack/lib/*.jar'],
		'core/rpc_server/pack/bin' :['core/rpc_server/pack/bin/*']
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
