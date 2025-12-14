"""
Setup configuration for Agentra.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agentra",
    version="0.1.0",
    author="Ayush Bhardwaj",
    author_email="classicayush@gmail.com",
    description="Live Agent Instrumentation & Evaluation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hastagab/agentra",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        # No hard dependencies - all optional
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.18.0"],
        "crewai": ["crewai>=0.1.0"],
        "langchain": ["langchain>=0.1.0", "langchain-core>=0.1.0"],
        "langgraph": ["langgraph>=0.0.1"],
        "autogen": ["pyautogen>=0.2.0"],
        "litellm": ["litellm>=1.0.0"],
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.18.0",
            "crewai>=0.1.0",
            "langchain>=0.1.0",
            "langchain-core>=0.1.0",
            "langgraph>=0.0.1",
            "pyautogen>=0.2.0",
            "litellm>=1.0.0",
        ],
    },
)

