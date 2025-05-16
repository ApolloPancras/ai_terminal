#!/usr/bin/env python3
"""
AI Terminal 安装脚本
"""

from setuptools import setup, find_packages

# 读取 README.md 作为长描述
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取依赖
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="ai_terminal",
    version="0.1.0",
    author="AI Terminal Team",
    author_email="pancras.lpb@gmail.com",
    description="智能终端助手，为 macOS 用户在 zsh 环境下提供交互式 AI 功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai_terminal",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ai_terminal=src.main:main",
            "ai-install=scripts.install:install_ai_terminal",
            "ai-uninstall=scripts.uninstall:main"
        ],
    },
    package_dir={"": "."},  # 告诉 setuptools 在根目录查找包
    packages=find_packages(include=['src', 'scripts']),  # 包含 src 和 scripts 包
    scripts=[
        'scripts/install.py',
        'scripts/uninstall.py',
        'scripts/setup_config.py'
    ],
    include_package_data=True,
    package_data={
        "ai_terminal": ["*"],
    },
)
