#!/usr/bin/env python3
"""
ZSH 集成模块
负责将 AI Terminal 集成到用户的 ZSH 环境中
"""

import os
import subprocess
from pathlib import Path


def install_zsh_integration():
    """
    在用户的 ZSH 配置中安装必要的钩子函数
    """
    # 用户的 ZSH 配置文件路径
    zshrc_path = os.path.expanduser("~/.zshrc")
    
    # 确保 AI Terminal 目录存在
    ai_terminal_dir = os.path.expanduser("~/.ai_terminal")
    os.makedirs(ai_terminal_dir, exist_ok=True)
    
    # 钩子函数内容
    hooks_content = """
# AI Terminal 集成
# 添加于 $(date)

# AI 命令函数
ai() {
  local ai_terminal_cmd
  if [ -f "$HOME/.ai_terminal/bin/ai_terminal" ]; then
    ai_terminal_cmd="$HOME/.ai_terminal/bin/ai_terminal"
  else
    ai_terminal_cmd="python -m src.main"
  fi
  
  if [ "$#" -eq 0 ]; then
    $ai_terminal_cmd
  else
    $ai_terminal_cmd "$@"
  fi
}

# 命令捕获钩子
# 用于收集历史命令和环境信息
ai_terminal_preexec() {
  # 记录命令执行前的工作目录和命令
  echo "$(pwd)|$(date +%s)|$1" >> "$HOME/.ai_terminal/cmd_history.log"
}

# 集成到 ZSH 钩子系统
if [[ ! " ${preexec_functions[@]} " =~ " ai_terminal_preexec " ]]; then
  preexec_functions+=(ai_terminal_preexec)
fi

# 环境信息收集
ai_terminal_update_env() {
  # 每小时更新一次环境信息
  local env_file="$HOME/.ai_terminal/env_info.log"
  local current_time=$(date +%s)
  local update_interval=3600  # 1小时
  
  # 检查是否需要更新
  if [[ ! -f "$env_file" ]] || (( $(date +%s) - $(stat -f %m "$env_file") > update_interval )); then
    echo "PATH=$PATH" > "$env_file"
    echo "USER=$USER" >> "$env_file"
    echo "HOME=$HOME" >> "$env_file"
    echo "SHELL=$SHELL" >> "$env_file"
    echo "TERM=$TERM" >> "$env_file"
    echo "LANG=$LANG" >> "$env_file"
    echo "OSTYPE=$OSTYPE" >> "$env_file"
    echo "HOSTNAME=$(hostname)" >> "$env_file"
    
    # 收集系统版本信息
    if command -v sw_vers &> /dev/null; then
      echo "MACOS_VERSION=$(sw_vers -productVersion)" >> "$env_file"
    fi
    
    # 收集 shell 版本信息
    echo "ZSH_VERSION=$ZSH_VERSION" >> "$env_file"
  fi
}

# 定期更新环境信息
ai_terminal_update_env

# Tab 补全功能
_ai_terminal_completion() {
  # 如果实现了自动补全功能，将在这里激活
  if [ -f "$HOME/.ai_terminal/completions.zsh" ]; then
    source "$HOME/.ai_terminal/completions.zsh"
  fi
}

# 注册补全函数
compdef _ai_terminal_completion ai
"""
    
    # 检查是否已经安装了钩子
    if os.path.exists(zshrc_path):
        with open(zshrc_path, "r") as f:
            content = f.read()
        if "# AI Terminal 集成" in content:
            print("ZSH 集成已经安装。")
            return
    
    # 添加钩子到 .zshrc
    with open(zshrc_path, "a") as f:
        f.write(hooks_content)
    
    # 创建必要的文件
    Path(os.path.join(ai_terminal_dir, "cmd_history.log")).touch(exist_ok=True)
    Path(os.path.join(ai_terminal_dir, "env_info.log")).touch(exist_ok=True)
    
    print("ZSH 集成安装成功!")
    print("请执行 'source ~/.zshrc' 或重启终端以激活功能。")


def create_completion_script():
    """创建命令补全脚本"""
    completion_file = os.path.expanduser("~/.ai_terminal/completions.zsh")
    
    completion_content = """
# AI Terminal 自动补全脚本

# 基本命令补全
_ai_commands() {
  local -a commands
  commands=(
    'help:显示帮助信息'
    'conversation:启动对话模式'
    'command:启动命令模式'
    'document:启动文档模式'
    'version:显示版本信息'
    'config:管理配置'
  )
  _describe -t commands 'ai commands' commands
}

# AI Terminal 补全函数
_ai_terminal_completion() {
  local curcontext="$curcontext" state line
  typeset -A opt_args
  
  _arguments \
    '1: :_ai_commands' \
    '*:: :->args'
  
  case $state in
    args)
      case $line[1] in
        config)
          _arguments \
            '1:config options:(show edit reset)'
          ;;
        *)
          _message 'no more arguments'
          ;;
      esac
      ;;
  esac
}

compdef _ai_terminal_completion ai
"""
    
    # 创建补全脚本
    with open(completion_file, "w") as f:
        f.write(completion_content)
    
    print("命令补全脚本已创建: %s" % completion_file)


if __name__ == "__main__":
    install_zsh_integration()
    create_completion_script()
