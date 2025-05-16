#!/usr/bin/env python3
"""
AI Terminal 配置文件设置脚本

此脚本帮助用户设置 AI Terminal 的配置文件。
"""

import os
import shutil
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def setup_config():
    """设置配置文件"""
    try:
        # 确定配置目录
        config_dir = Path.home() / ".ai_terminal"
        config_dir.mkdir(exist_ok=True, mode=0o700)  # 确保目录权限安全
        
        # 配置文件路径
        config_path = config_dir / "config.yaml"
        example_config = Path(__file__).parent.parent / "config" / "config.example.yaml"
        
        # 如果配置文件已存在，询问是否覆盖
        if config_path.exists():
            print(f"配置文件已存在于: {config_path}")
            if not input("是否覆盖现有配置? (y/N): ").lower() == 'y':
                print("已取消配置设置。")
                return
        
        # 复制示例配置文件
        if example_config.exists():
            shutil.copy(example_config, config_path)
            print(f"配置文件已创建: {config_path}")
            print("\n请编辑该文件以配置您的 API 密钥和其他设置。")
            
            # 检查 API 密钥
            if not os.environ.get("MISTRAL_API_KEY"):
                print("\n警告: 未检测到 MISTRAL_API_KEY 环境变量。")
                print("请设置环境变量或直接在配置文件中设置 api_key。")
        else:
            print("错误: 示例配置文件未找到。")
            sys.exit(1)
            
    except Exception as e:
        print(f"设置配置文件时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=== AI Terminal 配置设置 ===\n")
    setup_config()
