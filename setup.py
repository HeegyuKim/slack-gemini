from setuptools import setup, find_packages

setup(
    name="slack-gemini",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "slack-bolt",
        "slack-sdk",
        "python-dotenv",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "slack-gemini=slack_gemini.cli:main",
        ],
    },
)
