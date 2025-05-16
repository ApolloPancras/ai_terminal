#!/usr/bin/env python3
"""
命令处理器模块
负责处理命令生成、解释和优化相关请求
"""

import os
import re
import subprocess
from src.handlers.base_handler import BaseHandler
from src.utils.config_manager import MistralConfigManager


class CommandHandler(BaseHandler):
    """处理命令相关请求的处理器"""
    
    def handle(self, user_input):
        """
        处理用户的命令相关请求
        
        Args:
            user_input (str): 用户输入
            
        Returns:
            str: 处理结果
        """
        # 获取命令模式的配置
        config = MistralConfigManager.MODES["command"]
        
        # 构建上下文
        context = self.context_manager.build_context_for_mistral("command")
        
        # 添加环境信息到上下文
        self._enrich_context_with_environment(context)
        
        # 检测请求类型
        request_type = self._detect_request_type(user_input)
        
        # 根据不同的请求类型处理
        if request_type == "explain":
            # 解释命令
            command = self._extract_command(user_input)
            return self._explain_command(command, context)
        elif request_type == "generate":
            # 生成命令
            return self._generate_command(user_input, context)
        elif request_type == "optimize":
            # 优化命令
            command = self._extract_command(user_input)
            return self._optimize_command(command, context)
        else:
            # 一般命令相关查询
            return self._handle_general_command_query(user_input, context)
    
    def _detect_request_type(self, user_input):
        """
        检测命令请求的类型
        
        Args:
            user_input (str): 用户输入
            
        Returns:
            str: 请求类型 (explain, generate, optimize, general)
        """
        text = user_input.lower()
        
        if any(kw in text for kw in ["解释", "explain", "what does", "什么意思", "怎么理解"]):
            return "explain"
        elif any(kw in text for kw in ["生成", "创建", "generate", "create", "写一个"]):
            return "generate"
        elif any(kw in text for kw in ["优化", "改进", "optimize", "improve", "更好"]):
            return "optimize"
        else:
            return "general"
    
    def _extract_command(self, user_input):
        """
        从用户输入中提取命令
        
        Args:
            user_input (str): 用户输入
            
        Returns:
            str: 提取的命令
        """
        # 尝试查找引号中的命令
        matches = re.findall(r'[\'"]([^\'"]*)[\'""]', user_input)
        if matches:
            return matches[0]
        
        # 尝试查找解释/优化关键词后面的内容
        patterns = [
            r'解释\s+(.+)$', 
            r'explain\s+(.+)$',
            r'优化\s+(.+)$',
            r'optimize\s+(.+)$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_input)
            if match:
                return match.group(1)
        
        # 如果没有找到明确的命令，返回空字符串
        return ""
    
    def _explain_command(self, command, context):
        """
        解释命令
        
        Args:
            command (str): 要解释的命令
            context (dict): 上下文
            
        Returns:
            str: 解释结果
        """
        if not command:
            return "我需要一个具体的命令来解释。请提供要解释的具体命令。"
        
        # 更新上下文
        context["action"] = "explain"
        context["command"] = command
        
        # 构建提示
        prompt = f"请详细解释这个命令的功能和用法：`{command}`。包括各个参数的作用和可能的使用场景。"
        
        # 调用 LLM 生成解释
        config = MistralConfigManager.MODES["command"]
        explanation = self.llm_client.generate_response(
            prompt, 
            context,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            top_p=config["top_p"]
        )
        
        return explanation
    
    def _generate_command(self, user_input, context):
        """
        生成命令
        
        Args:
            user_input (str): 用户输入
            context (dict): 上下文
            
        Returns:
            str: 生成的命令
        """
        # 更新上下文
        context["action"] = "generate"
        context["requirement"] = user_input
        
        # 构建提示
        prompt = f"根据以下需求生成适合 macOS 和 zsh 的命令：{user_input}"
        
        # 调用 LLM 生成命令
        config = MistralConfigManager.MODES["command"]
        result = self.llm_client.generate_response(
            prompt, 
            context,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            top_p=config["top_p"]
        )
        
        return result
    
    def _optimize_command(self, command, context):
        """
        优化命令
        
        Args:
            command (str): 要优化的命令
            context (dict): 上下文
            
        Returns:
            str: 优化结果
        """
        if not command:
            return "我需要一个具体的命令来优化。请提供要优化的具体命令。"
        
        # 更新上下文
        context["action"] = "optimize"
        context["command"] = command
        
        # 构建提示
        prompt = f"请优化下面这个命令，让它更高效、更安全，并解释优化理由：`{command}`"
        
        # 调用 LLM 生成优化结果
        config = MistralConfigManager.MODES["command"]
        optimization = self.llm_client.generate_response(
            prompt, 
            context,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            top_p=config["top_p"]
        )
        
        return optimization
    
    def _handle_general_command_query(self, user_input, context):
        """
        处理一般命令相关查询
        
        Args:
            user_input (str): 用户输入
            context (dict): 上下文
            
        Returns:
            str: 处理结果
        """
        # 调用 LLM 生成回复
        config = MistralConfigManager.MODES["command"]
        response = self.llm_client.generate_response(
            user_input, 
            context,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            top_p=config["top_p"]
        )
        
        return response
    
    def _enrich_context_with_environment(self, context):
        """
        用环境信息丰富上下文
        
        Args:
            context (dict): 上下文
        """
        # 添加当前工作目录
        context["current_directory"] = os.getcwd()
        
        # 添加重要的环境变量
        context["env_vars"] = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", ""),
            "USER": os.environ.get("USER", ""),
            "SHELL": os.environ.get("SHELL", "")
        }
        
        # 添加系统信息
        try:
            # 获取 macOS 版本
            process = subprocess.run(["sw_vers", "-productVersion"], capture_output=True, text=True, check=False)
            context["macos_version"] = process.stdout.strip() if process.returncode == 0 else "Unknown"
            
            # 获取 zsh 版本
            process = subprocess.run(["zsh", "--version"], capture_output=True, text=True, check=False)
            context["zsh_version"] = process.stdout.strip() if process.returncode == 0 else "Unknown"
        except Exception:
            context["macos_version"] = "Unknown"
            context["zsh_version"] = "Unknown"
