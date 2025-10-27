"""Setup script for SenseTop package"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sensetop",
    version="0.1.0-dev",
    author="Ryan RBW",
    description="Real-time monitoring application for Sense HAT on Raspberry Pi 5",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ryan-rbw/sensetop",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console :: Curses",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=[
        "sense-hat>=2.2.0",
        "smbus2>=0.4.1",
        "numpy>=1.19.0",
        "pytz>=2021.1",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.12.0",
            "pytest-asyncio>=0.18.0",
            "mypy>=0.910",
            "pylint>=2.10.0",
            "flake8>=4.0.0",
            "black>=21.9b0",
            "isort>=5.9.0",
        ],
        "viz": [
            "plotext>=5.0.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sensetop=sensetop.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
