#!/usr/bin/env python3
"""
Rails Migration Assistant - Setup Configuration
"""

from setuptools import setup, find_packages
import pathlib

# Read the contents of README file
this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="rails-migration-assistant",
    version="1.0.0",
    author="Mohammed Hassan",
    author_email="mohamed.hassan2022s@gmail.com",
    description="AI-powered Rails upgrade assistance with dual LLM support for secure modernization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mohamed7456/rails-migration-assistant",
    project_urls={
        "Bug Tracker": "https://github.com/mohamed7456/rails-migration-assistant/issues",
        "Documentation": "https://github.com/mohamed7456/rails-migration-assistant#readme",
        "Source Code": "https://github.com/mohamed7456/rails-migration-assistant",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Ruby",
        "Framework :: Flask",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies
        "numpy>=1.21.0",
        "sentence-transformers>=2.2.0",
        "faiss-cpu>=1.7.0",
        "gitpython>=3.1.0",
        "python-dotenv>=0.19.0",
        
        # AI/ML Models
        "google-generativeai>=0.3.0",
        "transformers>=4.35.0",
        "torch>=2.0.0",
        "bitsandbytes>=0.41.0",
        "accelerate>=0.20.0",
        
        # Data Processing & Web
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "lxml>=4.6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
        ],
        "gui": [
            "tkinter-page>=7.0.0",
        ],
        "performance": [
            "auto-gptq>=0.4.0",
            "optimum>=1.12.0",
            "flash-attn>=2.0.0",
            "xformers>=0.0.20",
        ],
    },
    entry_points={
        "console_scripts": [
            "rails-migrate=rails_upgrade_suggestions:main",
            "rails-gui=rails_upgrade_gui:main",
        ],
    },
    include_package_data=True,
    package_data={
        "rails_migration_assistant": [
            "data/*.jsonl",
            "data/*.index",
            "data/docs/**/*.md",
            "examples/*.json",
            "examples/*.patch",
        ],
    },
    keywords=[
        "rails", "ruby", "upgrade", "migration", "ai", "llm", 
        "modernization", "automation", "assistant", "gemini", "local-llm"
    ],
    zip_safe=False,
)
