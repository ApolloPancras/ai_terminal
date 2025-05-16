#!/usr/bin/env python3
"""
对话处理器模块
负责处理一般性对话交互
"""

from src.handlers.base_handler import BaseHandler
from src.utils.config_manager import MistralConfigManager


class ConversationHandler(BaseHandler):
    """处理一般性对话的处理器"""
    
    def handle(self, user_input):
        """
        处理用户的对话输入
        
        Args:
            user_input (str): 用户输入
            
        Returns:
            str: 处理结果
        """
        # 获取对话模式的配置
        config = MistralConfigManager.MODES["conversation"]
        
        # 构建上下文
        context = self.context_manager.build_context_for_mistral("conversation")
        
        # 调用 LLM 生成回复
        response = self.llm_client.generate_response(
            user_input, 
            context,
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            top_p=config["top_p"]
        )
        
        return response
