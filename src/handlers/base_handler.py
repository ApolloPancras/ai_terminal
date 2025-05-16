#!/usr/bin/env python3
"""
基础处理器模块
定义了各种处理器的基类，提供通用功能
"""


class BaseHandler:
    """处理用户请求的基础类"""
    
    def __init__(self, llm_client, context_manager, settings=None):
        """
        初始化基础处理器
        
        Args:
            llm_client: LLM 客户端
            context_manager: 上下文管理器
            settings (dict): 配置参数
        """
        self.llm_client = llm_client
        self.context_manager = context_manager
        self.settings = settings or {}
        
    def handle(self, user_input):
        """
        处理用户输入
        
        Args:
            user_input (str): 用户输入
            
        Returns:
            str: 处理结果
        """
        raise NotImplementedError("子类必须实现此方法")
