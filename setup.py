# -*- coding: utf-8 -*-
from pdf_on_submit import __version__ as version
from setuptools import find_packages, setup

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

setup(
	name="pdf_on_submit",
	version=version,
	description="Print to PDF on submit of a doctype",
	author="ALYF GmbH",
	author_email="hallo@alyf.de",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires,
)
