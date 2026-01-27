#!/usr/bin/env python3
"""
Setup script for Church Media Automation System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="church-media-automation",
    version="1.0.0",
    author="Church Media Team",
    description="A modular media workflow system for churches",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/church-media-automation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Religion",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "pillow>=10.0.0",
        "requests>=2.31.0",
        "watchdog>=3.0.0",
    ],
    extras_require={
        "obs": ["obs-websocket-py>=1.0"],
        "whisperx": ["whisperx>=3.0.0", "faster-whisper>=0.9.0"],
        "youtube": [
            "google-api-python-client>=2.100.0",
            "google-auth-oauthlib>=1.1.0",
            "google-auth-httplib2>=0.1.1",
        ],
        "dev": [
            "pytest>=7.4.0",
            "black>=23.9.0",
            "flake8>=6.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cmas=controller.workflow_controller:main",
        ],
    },
)
