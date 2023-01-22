from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in my_app/__init__.py
from my_app import __version__ as version

setup(
	name="my_app",
	version=version,
	description="about pos",
	author="Admin",
	author_email="admin@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
