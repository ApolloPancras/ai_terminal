#!/usr/bin/env python3
"""
配置管理器模块
负责管理系统的配置参数，包括 Mistral API 参数、模式检测等
"""

import re


class MistralConfigManager:
    """管理 Mistral 模型的配置设置"""
    
    MODES = {
        "conversation": {
            "system_prompt": """你是 AI Terminal，一个智能终端助手，专注于在命令行环境中提供帮助。
当用户提问时：
1. 提供简洁、准确、有帮助的答案
2. 保持回答的技术准确性
3. 适应用户的技术水平，不过分简化也不过度复杂化
4. 当有多种可能的解释时，先提供最可能的答案，再提及其他可能性
5. 回答保持简洁，除非用户明确要求详细解释

避免：长篇大论、不必要的礼貌用语、重复问题内容""",
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": 0.9,
            "frequency_penalty": 0.2,
            "presence_penalty": 0.2
        },
        "command": {
            "system_prompt": """你是 AI Terminal 的命令专家组件，专注于 macOS/zsh 环境下的命令行辅助。
你的职责包括：
1. 根据用户意图生成精确的 shell 命令
2. 清晰解释命令的功能、参数和预期结果
3. 识别命令中的潜在错误或效率问题
4. 提供命令优化建议，考虑安全性和效率
5. 维护用户当前的环境上下文（工作目录、环境变量等）

遵循以下规则：
- 命令必须适用于 macOS 和 zsh
- 优先考虑内置命令和常见工具
- 涉及系统更改的命令必须包含警告
- 对复杂命令提供分步解释
- 当命令可能失败时，提供故障排除建议""",
            "temperature": 0.4,
            "max_tokens": 512,
            "top_p": 0.8,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.2
        },
        "document": {
            "system_prompt": """你是 AI Terminal 的文档分析组件，专注于文件内容的处理和分析。
你的职责包括：
1. 根据用户需求分析和总结文件内容
2. 提取文档中的关键信息和见解
3. 整理和格式化输出以提高可读性
4. 针对特定文件类型提供专业分析（代码、配置文件、日志等）
5. 在必要时跨文件关联信息

工作方式：
- 优先处理用户明确指出的关注点
- 区分事实性内容和推断性分析
- 对大型文档提供分层次的摘要
- 针对技术文档突出关键配置和参数
- 保持客观，除非用户要求主观评估""",
            "temperature": 0.3,
            "max_tokens": 2048,
            "top_p": 0.85,
            "frequency_penalty": 0.3,
            "presence_penalty": 0.1
        }
    }
    
    @staticmethod
    def detect_mode(user_input, current_context=None):
        """
        根据用户输入和当前上下文检测最适合的模式
        
        Args:
            user_input (str): 用户输入
            current_context (dict): 当前上下文
            
        Returns:
            str: 检测到的模式 (conversation, command, document)
        """
        # 检测命令模式（请求与命令相关的帮助）
        command_patterns = [
            r'如何.*命令', r'怎么用.*命令', r'解释.*命令',
            r'生成.*命令', r'运行.*命令', r'执行.*命令',
            r'命令.*什么意思', r'command', r'cmd', r'shell'
        ]
        
        # 检测文档模式（涉及文件操作）
        document_patterns = [
            r'分析.*文件', r'总结.*文件', r'读取.*文件',
            r'文件内容', r'文档', r'summarize', r'document'
        ]
        
        # 简单模式检测实现
        for pattern in command_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return "command"
                
        for pattern in document_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return "document"
        
        # 默认为对话模式
        return "conversation"
    
    @classmethod
    def get_config_for_input(cls, user_input, current_context=None):
        """
        获取适合当前输入的配置
        
        Args:
            user_input (str): 用户输入
            current_context (dict): 当前上下文
            
        Returns:
            dict: 配置参数
        """
        mode = cls.detect_mode(user_input, current_context)
        return cls.MODES[mode]
