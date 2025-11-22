"""
ATON Format - Adaptive Token-Oriented Notation
Setup configuration for PyPI package
"""

from setuptools import setup, find_packages
import os

# Read version from version.py
version = {}
with open(os.path.join("src", "aton_format", "version.py")) as f:
    exec(f.read(), version)

# Read long description from README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="aton-format",
    version=version["__version__"],
    author="Stefano D'Agostino",
    author_email="dago.stefano@gmail.com",
    description="ATON FORMAT Advanced data serialization achieving 50-60% token reduction with Compression Modes, SQL-like Query Language, and Streaming Support for LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dagoSte/aton-format",
    project_urls={
        "Bug Tracker": "https://github.com/dagoSte/aton-format/issues",
        "Documentation": "https://www.atonformat.com/documentation.html",
        "Source Code": "https://github.com/dagoSte/aton-format",
        "Changelog": "https://github.com/dagoSte/aton-format/blob/main/CHANGELOG.md",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - pure Python!
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    keywords=[
        "aton",
        "llm",
        "large language models",
        "token optimization",
        "data serialization",
        "json alternative",
        "compression",
        "query language",
        "streaming",
        "ai",
        "machine learning",
        "gpt",
        "claude",
        "openai",
        "anthropic",
    ],
    include_package_data=True,
    zip_safe=False,
)