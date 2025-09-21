from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="trade-analysis-dhan",
    version="1.0.0",
    author="Vikky Sarswat",
    author_email="vikky.sarswat@gmail.com",
    description="AI-powered trading analysis using local LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vikkysarswat/trade_analysis_dhan",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.1.0",
        "numpy>=1.24.3",
        "matplotlib>=3.7.2",
        "seaborn>=0.12.2",
        "requests>=2.31.0",
        "pyyaml>=6.0.1",
        "scikit-learn>=1.3.0",
        "jinja2>=3.1.2",
    ],
    entry_points={
        "console_scripts": [
            "trading-analyzer=main:main",
        ],
    },
)
