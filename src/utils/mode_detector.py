#!/usr/bin/env python3
"""
模式检测器
根据用户输入和上下文自动检测当前应该使用哪种模式
"""

import os
import re


def detect_mode(user_input, current_context=None):
    """
    检测用户输入应该使用哪种模式处理
    
    Args:
        user_input (str): 用户输入
        current_context (dict): 当前上下文
        
    Returns:
        str: 模式名称 (conversation, command, document)
    """
    # 如果包含文件路径并且文件存在，可能是文档模式
    file_paths = extract_potential_file_paths(user_input)
    for file_path in file_paths:
        if os.path.exists(file_path):
            # 检查是否有文档相关的动作词
            if has_document_action_verb(user_input):
                return "document"
    
    # 检测是否是命令相关的请求
    if is_command_related(user_input):
        return "command"
    
    # 默认为对话模式
    return "conversation"


def extract_potential_file_paths(text):
    """
    从文本中提取可能的文件路径
    
    Args:
        text (str): 输入文本
        
    Returns:
        list: 可能的文件路径列表
    """
    paths = []
    
    # 匹配绝对路径
    abs_paths = re.findall(r'/[\w\./\-_]+', text)
    paths.extend(abs_paths)
    
    # 匹配相对路径
    rel_paths = re.findall(r'[\w\-_]+\.\w+', text)
    paths.extend(rel_paths)
    
    # 匹配带有 ~ 的路径
    home_paths = re.findall(r'~[\w\./\-_]+', text)
    paths.extend([os.path.expanduser(p) for p in home_paths])
    
    return paths


def has_document_action_verb(text):
    """
    检查文本是否包含与文档处理相关的动作词
    
    Args:
        text (str): 输入文本
        
    Returns:
        bool: 是否包含文档处理相关的动作词
    """
    # 文档处理相关的动作词
    document_verbs = [
        '分析', '总结', '概括', '摘要', '阅读', '读取', '处理',
        'analyze', 'summarize', 'read', 'process', 'extract',
        'summarise', 'examine', 'review'
    ]
    
    # 将文本转换为小写以进行不区分大小写的匹配
    text_lower = text.lower()
    
    # 检查是否包含任何文档处理相关的动作词
    return any(verb.lower() in text_lower for verb in document_verbs)


def is_command_related(text):
    """
    检查文本是否与命令相关
    
    Args:
        text (str): 输入文本
        
    Returns:
        bool: 是否与命令相关
    """
    # 命令相关的模式
    command_patterns = [
        r'如何.*命令', r'怎么用.*命令', r'解释.*命令',
        r'生成.*命令', r'运行.*命令', r'执行.*命令',
        r'命令.*什么意思', r'command', r'cmd', r'shell',
        r'如何在终端', r'help me', r'how to .*在终端',
        r'terminal', r'console', r'怎样才能', r'写一个脚本'
    ]
    
    # 将文本转换为小写以进行不区分大小写的匹配
    text_lower = text.lower()
    
    # 检查是否匹配任何命令相关的模式
    return any(re.search(pattern, text_lower) for pattern in command_patterns)
