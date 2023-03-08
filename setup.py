#!/usr/bin/env python

from setuptools import find_packages, setup


def main():
    return setup(
        author="Sijin Zhang",
        author_email="zsjzyhzp@gmail.com",
        version="0.0.1",
        description="ESR task",
        maintainer="Sijin",
        maintainer_email="zsjzyhzp@gmail.com",
        name="esr task",
        packages=find_packages(),
        data_files=[],
        zip_safe=False,
    )


if __name__ == "__main__":
    main()
