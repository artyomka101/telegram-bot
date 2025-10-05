from setuptools import setup, find_packages

setup(
    name="telegram-bot",
    version="1.0.0",
    description="Telegram bot application",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot==21.3",
        "python-dotenv==1.0.1",
    ],
    python_requires=">=3.11",
)
