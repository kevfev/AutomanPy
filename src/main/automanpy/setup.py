#!/usr/bin/env python

from setuptools import setup, find_packages, Command
from os import path, system

class CleanCommand(Command):
    """
    Custom clean command to tidy up the project root.
    Teken from: https://stackoverflow.com/questions/3779915/why-does-python-setup-py-sdist-create-unwanted-project-egg-info-in-project-r
    """
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')

with open("README.md", "r") as fh:
	ld = fh.read()

setup(name = 'automanpy',
	version= '0.4.2.a0',
	description = 'Python bindings for AutoMan Runtime. Software is current in development, and not properly tested.',
	author = 'Kevin Feveck',
	cmdclass={
        'clean': CleanCommand,
    },
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

