# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='rivertrace',
    version='0.1.0',
    description='Identifies rivers in satellite images and generates a profile of pixel values along its length.',
    long_description=readme,
    author='James Runnalls',
    author_email='james.runnalls@eawag.ch',
    url='https://github.com/JamesRunnalls/river-trace',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
