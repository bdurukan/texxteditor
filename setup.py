"""
Setup script for installing the TeXXtEditor package.
"""
import os
from setuptools import setup, find_packages

# Read the content of README.md if it exists
readme = ""
if os.path.exists('README.md'):
    with open('README.md', 'r', encoding='utf-8') as f:
        readme = f.read()

setup(
    name="texxteditor",
    version="1.0.0",
    description="A Microsoft Word-like text editor with A4 page format",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="TeXXtEditor Team",
    author_email="example@texxteditor.com",
    url="https://github.com/texxteditor/texxteditor",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Text Editors",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires='>=3.7',
    install_requires=[
        "pyaudio>=0.2.11",
        "pydub>=0.25.1",
        "sounddevice>=0.4.1",
        "keyboard>=0.13.5",
        "numpy>=1.19.5",
        "requests>=2.25.1",
    ],
    entry_points={
        'console_scripts': [
            'texxteditor=texxteditor.main:main',
        ],
        'gui_scripts': [
            'texxteditor-gui=texxteditor.main:main',
        ],
    },
)
