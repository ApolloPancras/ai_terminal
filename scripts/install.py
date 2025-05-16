#!/usr/bin/env python3
"""
AI Terminal 安装脚本
负责安装 AI Terminal 并设置必要的环境
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.zsh_integration.install import install_zsh_integration, create_completion_script
from src.utils.config_loader import create_default_config


def install_ai_terminal():
    """
    安装 AI Terminal
    """
    print("开始安装 AI Terminal...")
    
    # 确保 AI Terminal 目录存在
    ai_terminal_dir = os.path.expanduser("~/.ai_terminal")
    bin_dir = os.path.join(ai_terminal_dir, "bin")
    os.makedirs(bin_dir, exist_ok=True)
    
    # 获取当前脚本目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 创建符号链接或复制文件到 ~/.ai_terminal 目录
    try:
        # 如果在开发环境，创建符号链接
        if os.path.exists(os.path.join(current_dir, "setup.py")):
            print("检测到开发环境，创建符号链接...")
            for item in ["src", "requirements.txt"]:
                src = os.path.join(current_dir, item)
                dst = os.path.join(ai_terminal_dir, item)
                if os.path.exists(dst):
                    if os.path.islink(dst):
                        os.unlink(dst)
                    elif os.path.isdir(dst):
                        shutil.rmtree(dst)
                    else:
                        os.remove(dst)
                os.symlink(src, dst)
        else:
            # 如果是安装包，复制文件
            print("复制文件到安装目录...")
            for item in ["src", "requirements.txt"]:
                src = os.path.join(current_dir, item)
                dst = os.path.join(ai_terminal_dir, item)
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst)
                    else:
                        os.remove(dst)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
    
        # 创建可执行脚本
        create_executable_script(bin_dir)
        
        # 创建默认配置
        config_path = os.path.join(ai_terminal_dir, "config.yaml")
        if not os.path.exists(config_path):
            create_default_config(config_path)
        
        # 安装 ZSH 集成
        install_zsh_integration()
        create_completion_script()
        
        # 安装依赖
        install_dependencies()
        
        print("\nAI Terminal 安装成功!")
        print("请确保设置了 Mistral API 密钥:")
        print("  export MISTRAL_API_KEY='your-api-key'")
        print("\n使用方法:")
        print("  ai 你好，请解释什么是 Docker")
        print("  ai 如何查找最近修改的文件")
        print("  ai 解释命令 ps aux | grep python")
        print("  ai 总结 ~/document.txt 的主要内容")
        
    except Exception as e:
        print(f"安装过程中出错: {str(e)}")
        return False
    
    return True


def create_executable_script(bin_dir):
    """
    创建可执行脚本
    
    Args:
        bin_dir (str): 可执行文件目录
    """
    script_path = os.path.join(bin_dir, "ai_terminal")
    
    script_content = """#!/usr/bin/env python3
import os
import sys

# 添加 AI Terminal 目录到 Python 路径
ai_terminal_dir = os.path.expanduser("~/.ai_terminal")
sys.path.insert(0, ai_terminal_dir)

# 导入并运行主程序
from src.main import main

if __name__ == "__main__":
    main()
"""
    
    # 写入脚本
    with open(script_path, "w") as f:
        f.write(script_content)
    
    # 设置可执行权限
    os.chmod(script_path, 0o755)


def install_dependencies():
    """
    安装依赖包
    """
    print("\n安装依赖...")
    
    requirements_path = os.path.expanduser("~/.ai_terminal/requirements.txt")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
        print("依赖安装成功。")
    except subprocess.CalledProcessError:
        print("依赖安装失败，请手动运行:")
        print(f"  pip install -r {requirements_path}")


if __name__ == "__main__":
    if install_ai_terminal():
        print("\n安装成功完成! 请重新启动终端或运行 'source ~/.zshrc' 以激活 AI Terminal。")
    else:
        print("\n安装失败。请查看上方错误信息。")
        sys.exit(1)
