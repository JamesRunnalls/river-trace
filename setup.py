# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='rivertrace',
    version='1.0.7',
    description='Identifies rivers in satellite images and generates a path of pixel values along its length.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='James Runnalls',
    author_email='runnalls.james@gmail.com',
    url='https://github.com/JamesRunnalls/river-trace',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
            'geopandas==0.9.0',
            'netCDF4==1.4.2',
            'scikit-image==0.17.2',
            'networkx==2.3.0',
            'shapely==1.6.4',
            'matplotlib',
            'numpy',
        ]
)