#!/usr/bin/env python3

import setuptools

with open("README.md", 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="tinytinypy",
    version='0.1',
    author="Felix Stupp",
    author_email="felix.stupp@outlook.com",
    description="Utility package for using API of Tiny Tiny RSS",
    long_description=long_description,
    url="https://github.com/Zocker1999NET/tinytinypy",
    python_requires='>=3.4',
    install_requires=[
        "pyxdg >=0.25",
    ],
    scripts=[
        "scripts/tinytinypy",
    ],
    packages=[
        "tinytinypy",
    ],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Utilities",
    ],
)
