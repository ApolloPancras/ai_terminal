#!/usr/bin/env python3
"""
AI Terminal 卸载脚本

此脚本用于完全卸载 AI Terminal 及其所有相关文件，包括：
- 主程序文件
- 配置文件
- 缓存文件
- 日志文件
- 临时文件
- ZSH 集成
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 需要删除的文件和目录列表
FILES_TO_REMOVE = [
    # 主目录
    os.path.expanduser("~/.ai_terminal"),
    
    # 日志文件
    os.path.expanduser("~/Library/Logs/ai_terminal"),
    
    # 缓存目录
    os.path.expanduser("~/Library/Caches/ai_terminal"),
    
    # 临时文件
    "/tmp/ai_terminal_*",
    
    # 旧版本可能的位置
    os.path.expanduser("~/.config/ai_terminal"),
    os.path.expanduser("~/.local/share/ai_terminal"),
]

# 需要清理的 ZSH 配置中的内容
ZSH_RC = os.path.expanduser("~/.zshrc")
ZSH_RC_BACKUP = os.path.expanduser("~/.zshrc.ai_terminal.bak")
ZSH_MARKER = "# AI Terminal 集成"

def confirm_uninstall():
    """确认是否继续卸载"""
    print("\n" + "=" * 50)
    print("AI Terminal 卸载程序")
    print("=" * 50)
    print("\n此操作将删除 AI Terminal 及其所有相关文件，包括：")
    print("  - 配置文件 (~/.ai_terminal/)")
    print("  - 日志文件 (~/Library/Logs/ai_terminal/)")
    print("  - 缓存文件 (~/Library/Caches/ai_terminal/)")
    print("  - 临时文件 (/tmp/ai_terminal_*)")
    print("  - ZSH 集成配置")
    
    response = input("\n确定要完全卸载 AI Terminal 吗？(y/N): ").strip().lower()
    return response == 'y'

def remove_zsh_integration():
    """从 ZSH 配置中删除集成代码"""
    if not os.path.exists(ZSH_RC):
        return False
    
    # 创建备份
    try:
        # 读取原始内容
        with open(ZSH_RC, 'r') as f:
            lines = f.readlines()
        
        # 查找 AI Terminal 相关的行
        start_idx = -1
        end_idx = -1
        in_section = False
        
        for i, line in enumerate(lines):
            if ZSH_MARKER in line:
                if start_idx == -1:  # 第一次找到标记
                    start_idx = i
                    in_section = True
                else:  # 第二次找到标记，表示结束
                    end_idx = i
                    in_section = False
            elif in_section and line.strip() == '':  # 空行结束部分
                if end_idx == -1:
                    end_idx = i
        
        # 如果找到了要删除的部分
        if start_idx != -1 and end_idx != -1:
            # 创建备份
            shutil.copy2(ZSH_RC, ZSH_RC_BACKUP)
            
            # 删除相关行
            new_lines = lines[:start_idx] + lines[end_idx+1:]
            
            # 写回文件
            with open(ZSH_RC, 'w') as f:
                f.writelines(new_lines)
            
            return True
    except Exception as e:
        print(f"警告: 清理 ZSH 配置时出错: {e}")
        return False
    
    return False

def remove_files():
    """删除所有相关文件"""
    removed = []
    errors = []
    
    for path_spec in FILES_TO_REMOVE:
        # 处理通配符
        import glob
        paths = glob.glob(os.path.expanduser(path_spec))
        
        for path in paths:
            try:
                if os.path.isfile(path) or os.path.islink(path):
                    os.remove(path)
                    removed.append(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    removed.append(path + "/")
            except Exception as e:
                errors.append(f"  删除 {path} 失败: {e}")
    
    return removed, errors

def main():
    """主函数"""
    if not confirm_uninstall():
        print("\n卸载已取消。")
        return
    
    print("\n开始卸载 AI Terminal...")
    
    # 1. 移除 ZSH 集成
    print("\n[1/3] 正在移除 ZSH 集成...")
    if remove_zsh_integration():
        print("  ✓ 已从 ~/.zshrc 中移除 AI Terminal 集成")
        print(f"  注意: 原始配置已备份到 {ZSH_RC_BACKUP}")
    else:
        print("  ! 未找到 ZSH 集成配置或移除失败")
    
    # 2. 删除文件
    print("\n[2/3] 正在删除文件...")
    removed, errors = remove_files()
    
    if removed:
        print("  已删除以下文件/目录:")
        for item in removed:
            print(f"    - {item}")
    else:
        print("  未找到要删除的文件")
    
    if errors:
        print("\n  发生以下错误:")
        for error in errors:
            print(f"    {error}")
    
    # 3. 清理其他残留
    print("\n[3/3] 正在清理其他残留...")
    
    # 清理命令历史
    try:
        history_db = os.path.expanduser("~/.ai_terminal/history.db")
        if os.path.exists(history_db):
            os.remove(history_db)
            print(f"  ✓ 已删除命令历史: {history_db}")
    except Exception as e:
        print(f"  ! 删除命令历史失败: {e}")
    
    # 清理 Python 缓存
    try:
        import glob
        cache_files = glob.glob(os.path.expanduser("~/.ai_terminal/__pycache__"))
        cache_files += glob.glob(os.path.expanduser("~/.ai_terminal/**/__pycache__", recursive=True))
        
        for cache_dir in cache_files:
            shutil.rmtree(cache_dir, ignore_errors=True)
        
        if cache_files:
            print(f"  ✓ 已清理 Python 缓存文件")
    except Exception as e:
        print(f"  ! 清理 Python 缓存时出错: {e}")
    
    print("\n" + "=" * 50)
    print("AI Terminal 卸载完成!")
    print("=" * 50)
    print("\n请注意: 您可能需要重新启动终端或运行以下命令使更改生效:")
    print("  source ~/.zshrc")
    print("\n如果您想完全重置所有设置，可以手动删除以下文件:")
    print(f"  - {os.path.expanduser('~/.zshrc.ai_terminal.bak')} (ZSH 配置备份)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n卸载被用户中断。")
        sys.exit(1)
    except Exception as e:
        print(f"\n卸载过程中发生错误: {e}")
        sys.exit(1)
