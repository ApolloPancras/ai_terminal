#!/usr/bin/env python3
"""
文档处理器模块
负责处理文档分析、总结等文件内容相关的请求
"""

import os
import re
from pathlib import Path
from src.handlers.base_handler import BaseHandler
from src.utils.config_manager import MistralConfigManager


class DocumentHandler(BaseHandler):
    """处理文档相关请求的处理器"""
    
    # 支持的文件类型及其最大大小(字节)
    SUPPORTED_FILE_TYPES = {
        # 文本和标记文件
        ".txt": 1024 * 1024,      # 1MB
        ".md": 1024 * 1024,       # 1MB
        ".json": 1024 * 1024,     # 1MB
        ".csv": 1024 * 1024,      # 1MB
        ".xml": 1024 * 1024,      # 1MB
        ".yaml": 1024 * 1024,     # 1MB
        ".yml": 1024 * 1024,      # 1MB
        
        # 编程语言文件
        ".py": 512 * 1024,        # 512KB
        ".js": 512 * 1024,        # 512KB
        ".java": 512 * 1024,      # 512KB
        ".c": 512 * 1024,         # 512KB
        ".cpp": 512 * 1024,       # 512KB
        ".h": 512 * 1024,         # 512KB
        ".html": 512 * 1024,      # 512KB
        ".css": 512 * 1024,       # 512KB
        ".sh": 512 * 1024,        # 512KB
        ".go": 512 * 1024,        # 512KB
        ".rs": 512 * 1024,        # 512KB
        
        # 配置文件
        ".ini": 256 * 1024,       # 256KB
        ".conf": 256 * 1024,      # 256KB
        ".config": 256 * 1024,    # 256KB
        ".properties": 256 * 1024,# 256KB
        ".toml": 256 * 1024,      # 256KB
        
        # 日志文件
        ".log": 2 * 1024 * 1024,  # 2MB
    }
    
    def handle(self, user_input):
        """
        处理用户的文档相关请求
        
        Args:
            user_input (str): 用户输入
            
        Returns:
            str: 处理结果
        """
        # 获取文档模式的配置
        config = MistralConfigManager.MODES["document"]
        
        # 构建上下文
        context = self.context_manager.build_context_for_mistral("document")
        
        # 提取文件路径
        file_path = self._extract_file_path(user_input)
        if not file_path:
            return "我无法识别您要操作的文件路径。请明确指定文件路径。"
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return f"文件路径 '{file_path}' 不存在，请检查路径是否正确。"
        
        # 检查文件类型是否支持
        if not self._is_file_type_supported(file_path):
            return f"不支持的文件类型。目前支持的文件类型有: {', '.join(self.SUPPORTED_FILE_TYPES.keys())}"
        
        # 检查文件大小是否超出限制
        if not self._check_file_size(file_path):
            extension = os.path.splitext(file_path)[1]
            max_size_mb = self.SUPPORTED_FILE_TYPES.get(extension, 0) / (1024 * 1024)
            return f"文件太大，超出了处理限制。{extension} 类型文件的最大支持大小为 {max_size_mb}MB。"
        
        # 读取文件内容
        try:
            content = self._read_file_content(file_path)
        except Exception as e:
            return f"读取文件时发生错误: {str(e)}"
        
        # 检测请求类型并分派
        action = self._detect_action(user_input)
        
        # 更新上下文
        context["file_path"] = file_path
        context["file_content"] = content
        context["action"] = action
        
        # 根据不同动作处理
        if action == "summarize":
            return self._summarize_document(content, user_input, context)
        elif action == "analyze":
            return self._analyze_document(content, user_input, context)
        elif action == "extract":
            return self._extract_information(content, user_input, context)
        else:
            # 默认处理
            return self._process_document(content, user_input, context)
    
    def _extract_file_path(self, text):
        """
        从文本中提取文件路径
        
        Args:
            text (str): 输入文本
            
        Returns:
            str: 文件路径或 None
        """
        # 尝试查找引号中的路径
        matches = re.findall(r'[\'"]([^\'"]*\.[\w]+)[\'""]', text)
        if matches:
            path = matches[0]
            # 处理路径中的 ~ 符号
            if path.startswith("~"):
                path = os.path.expanduser(path)
            return os.path.abspath(path)
        
        # 尝试查找常见文件扩展名的路径
        extensions = list(self.SUPPORTED_FILE_TYPES.keys())
        for ext in extensions:
            pattern = r'(\S+{})\b'.format(re.escape(ext))
            match = re.search(pattern, text)
            if match:
                path = match.group(1)
                # 处理路径中的 ~ 符号
                if path.startswith("~"):
                    path = os.path.expanduser(path)
                return os.path.abspath(path)
        
        return None
    
    def _is_file_type_supported(self, file_path):
        """
        检查文件类型是否支持
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            bool: 是否支持该文件类型
        """
        _, ext = os.path.splitext(file_path)
        return ext.lower() in self.SUPPORTED_FILE_TYPES
    
    def _check_file_size(self, file_path):
        """
        检查文件大小是否超出限制
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            bool: 文件大小是否在允许范围内
        """
        _, ext = os.path.splitext(file_path)
        max_size = self.SUPPORTED_FILE_TYPES.get(ext.lower(), 0)
        file_size = os.path.getsize(file_path)
        return file_size <= max_size
    
    def _read_file_content(self, file_path):
        """
        读取文件内容
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            str: 文件内容
        """
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        return content
    
    def _detect_action(self, text):
        """
        检测用户意图的动作类型
        
        Args:
            text (str): 输入文本
            
        Returns:
            str: 动作类型 (summarize, analyze, extract)
        """
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ["总结", "概括", "summarize", "summary"]):
            return "summarize"
        elif any(kw in text_lower for kw in ["分析", "analyze", "analysis"]):
            return "analyze"
        elif any(kw in text_lower for kw in ["提取", "extract", "抽取"]):
            return "extract"
        else:
            # 默认为总结
            return "summarize"
    
    def _summarize_document(self, content, user_input, context):
        """
        总结文档内容
        
        Args:
            content (str): 文件内容
            user_input (str): 用户输入
            context (dict): 上下文
            
        Returns:
            str: 总结结果
        """
        # 构建提示
        prompt = f"请对以下文件内容进行总结。内容如下:\n\n{content}"
        
        # 如果用户输入中包含具体要求，添加到提示中
        if "要点" in user_input or "关键点" in user_input or "key points" in user_input:
            prompt += "\n\n请以要点形式总结主要内容。"
        elif "摘要" in user_input or "abstract" in user_input:
            prompt += "\n\n请提供一个简短的摘要。"
        
        # 调用 LLM 生成总结
        config = MistralConfigManager.MODES["document"]
        summary = self.llm_client.generate_response(
            prompt, 
            context,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            top_p=config["top_p"]
        )
        
        # 如果文件是代码文件，保存分析结果到上下文
        file_path = context.get("file_path", "")
        if file_path and any(file_path.endswith(ext) for ext in [".py", ".js", ".java", ".c", ".cpp", ".go", ".rs"]):
            self.context_manager.add_document_context(file_path, summary=summary)
        
        return summary
    
    def _analyze_document(self, content, user_input, context):
        """
        分析文档内容
        
        Args:
            content (str): 文件内容
            user_input (str): 用户输入
            context (dict): 上下文
            
        Returns:
            str: 分析结果
        """
        file_path = context.get("file_path", "")
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # 根据文件类型构建专门的提示
        if file_ext in [".py", ".js", ".java", ".c", ".cpp", ".go", ".rs"]:
            # 代码文件分析
            prompt = f"请分析以下代码文件，包括功能、结构、关键组件和可能的问题。内容如下:\n\n{content}"
        elif file_ext in [".log"]:
            # 日志文件分析
            prompt = f"请分析以下日志文件，识别重要的事件、错误和模式。内容如下:\n\n{content}"
        elif file_ext in [".json", ".yaml", ".yml", ".xml", ".toml"]:
            # 配置文件分析
            prompt = f"请分析以下配置文件，解释主要配置项及其作用。内容如下:\n\n{content}"
        else:
            # 一般文本文件
            prompt = f"请深入分析以下文本内容，包括主题、结构和关键信息。内容如下:\n\n{content}"
        
        # 调用 LLM 生成分析
        config = MistralConfigManager.MODES["document"]
        analysis = self.llm_client.generate_response(
            prompt, 
            context,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            top_p=config["top_p"]
        )
        
        # 保存分析结果到上下文
        self.context_manager.add_document_context(file_path, analysis=analysis)
        
        return analysis
    
    def _extract_information(self, content, user_input, context):
        """
        从文档中提取特定信息
        
        Args:
            content (str): 文件内容
            user_input (str): 用户输入
            context (dict): 上下文
            
        Returns:
            str: 提取结果
        """
        # 尝试识别用户想要提取的信息类型
        extract_type = "general"
        if "日期" in user_input or "日志" in user_input or "date" in user_input.lower():
            extract_type = "dates"
        elif "邮箱" in user_input or "email" in user_input.lower():
            extract_type = "emails"
        elif "链接" in user_input or "网址" in user_input or "url" in user_input.lower():
            extract_type = "urls"
        elif "函数" in user_input or "方法" in user_input or "function" in user_input.lower() or "method" in user_input.lower():
            extract_type = "functions"
        
        # 构建提示
        if extract_type == "general":
            prompt = f"请从以下内容中提取关键信息:\n\n{content}\n\n具体提取需求: {user_input}"
        elif extract_type == "dates":
            prompt = f"请从以下内容中提取所有日期和时间信息:\n\n{content}"
        elif extract_type == "emails":
            prompt = f"请从以下内容中提取所有电子邮件地址:\n\n{content}"
        elif extract_type == "urls":
            prompt = f"请从以下内容中提取所有URL和网络链接:\n\n{content}"
        elif extract_type == "functions":
            prompt = f"请从以下代码中提取所有函数和方法定义，包括其参数和功能简述:\n\n{content}"
        
        # 调用 LLM 生成提取结果
        config = MistralConfigManager.MODES["document"]
        extraction = self.llm_client.generate_response(
            prompt, 
            context,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            top_p=config["top_p"]
        )
        
        return extraction
    
    def _process_document(self, content, user_input, context):
        """
        处理文档的一般请求
        
        Args:
            content (str): 文件内容
            user_input (str): 用户输入
            context (dict): 上下文
            
        Returns:
            str: 处理结果
        """
        # 构建提示
        prompt = f"基于以下文件内容回答问题或执行请求: '{user_input}'\n\n文件内容:\n{content}"
        
        # 调用 LLM 生成结果
        config = MistralConfigManager.MODES["document"]
        result = self.llm_client.generate_response(
            prompt, 
            context,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            top_p=config["top_p"]
        )
        
        return result
