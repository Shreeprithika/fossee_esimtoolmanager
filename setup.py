#!/usr/bin/env python3
"""
setup.py for eSim Automated Tool Manager
FOSSEE / eSim Semester Long Internship - Autumn 2026 / Winter Internship
Task 5: Automated Tool Manager
"""

from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read() if os.path.exists("README.md") else "eSim Automated Tool Manager"

setup(
    name="esim-tool-manager",
    version="1.0.0",
    author="eSim Contributor",
    author_email="contact-esim@fossee.in",
    description="Automated Tool and Dependency Management Suite for FOSSEE eSim EDA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FOSSEE/eSim",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "esim_tool_manager": ["manifest.json"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "esim-tools=esim_tool_manager.cli:main",
            "esim-tool-manager=esim_tool_manager.cli:main",
        ],
    },
)
