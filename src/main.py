#!/usr/bin/env python3
"""
AI Terminal - 智能终端助手
主程序入口文件，处理命令行参数和调用相应的功能模块
"""

import os
import sys
import click
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent))

from src.core.llm_client import MistralClient
from src.core.context_manager import ContextManager
from src.utils.config_loader import load_config
from src.handlers.command_handler import CommandHandler
from src.handlers.conversation_handler import ConversationHandler
from src.handlers.document_handler import DocumentHandler
from src.utils.mode_detector import detect_mode


@click.command()
@click.argument('query', nargs=-1)
@click.option('--mode', '-m', type=click.Choice(['conversation', 'command', 'document']), 
              help='强制指定运行模式')
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='指定配置文件路径')
@click.option('--verbose', '-v', is_flag=True, help='显示详细输出')
@click.option('--debug', '-d', is_flag=True, help='启用调试模式')
def main(query, mode, config, verbose, debug):
    """AI Terminal - 智能终端助手
    
    示例:
        ai 你好，请介绍一下自己
        ai 如何查找大于100MB的文件
        ai 解释 ls -la | grep "^d"
        ai 总结 ~/document.txt 的主要内容
    """
    # 加载配置
    config_path = config or os.path.expanduser("~/.ai_terminal/config.yaml")
    try:
        settings = load_config(config_path)
    except Exception as e:
        if debug:
            click.echo(f"加载配置失败: {str(e)}", err=True)
        settings = {}
    
    # 初始化上下文管理器
    context_manager = ContextManager(
        max_history=settings.get('terminal', {}).get('max_history', 20)
    )
    
    # 获取当前工作目录和环境变量
    cwd = os.getcwd()
    env_vars = {k: v for k, v in os.environ.items() if k.startswith('PATH') or k in ['HOME', 'USER', 'SHELL']}
    context_manager.update_environment(env_vars=env_vars, cwd=cwd)
    
    # 如果没有输入，显示帮助信息
    if not query:
        click.echo(main.get_help(click.Context(main)))
        return
    
    # 组合用户查询
    user_input = ' '.join(query)
    
    try:
        # 初始化 LLM 客户端
        llm_client = MistralClient(settings.get('api', {}))
        
        # 如果没有指定模式，自动检测
        if not mode:
            mode = detect_mode(user_input, context_manager.build_context_for_mistral())
            
        if verbose:
            click.echo(f"运行模式: {mode}", err=True)
        
        # 根据模式选择处理器
        if mode == 'command':
            handler = CommandHandler(llm_client, context_manager, settings)
        elif mode == 'document':
            handler = DocumentHandler(llm_client, context_manager, settings)
        else:  # 默认为对话模式
            handler = ConversationHandler(llm_client, context_manager, settings)
        
        # 处理请求并输出结果
        response = handler.handle(user_input)
        click.echo(response)
        
        # 更新上下文
        context_manager.update_context(user_input, response, mode)
        context_manager.save_context_to_disk()
        
    except Exception as e:
        if debug:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        else:
            click.echo(f"错误: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
