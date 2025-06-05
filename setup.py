from setuptools import setup, find_packages
import os
import re

def get_version():
    version_file = os.path.join(os.path.dirname(__file__), "src", "sendlayer", "version.py")
    with open(version_file, "r") as f:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sendlayer",
    version=get_version(),
    author="SendLayer",
    author_email="support@sendlayer.com",
    description="Official Python SDK for SendLayer API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sendlayer/sendlayer-python",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ]
) 