from setuptools import setup, find_packages

setup(
    name="lifelog-test-data",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0.2",
        "sqlalchemy>=2.0.36",
    ],
    entry_points={
        "console_scripts": [
            "manage-test-data=manage_test_data.cli:main",
        ],
    },
    python_requires=">=3.11",
    author="Your Name",
    description="LifeLogプロジェクトのテストデータ管理ツール",
    long_description=open("docs/test_data_cli_spec.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
)
