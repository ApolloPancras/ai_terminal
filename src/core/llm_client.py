#!/usr/bin/env python3
"""
Mistral API 客户端模块
处理与 Mistral API 的通信，包括请求生成、响应处理等
"""

import os
from mistralai import Mistral
from mistralai.models.chat_completion import ChatMessage


class MistralClient:
    """Mistral API 客户端类，负责与 Mistral API 通信"""
    
    def __init__(self, config=None):
        """
        初始化 Mistral 客户端
        
        Args:
            config (dict): 配置参数，包含 API 密钥、模型名称等
        """
        config = config or {}
        self.api_key = config.get('api_key') or os.environ.get("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("缺少 Mistral API 密钥。请设置环境变量 MISTRAL_API_KEY 或在配置文件中设置。")
        
        self.model = config.get('model', "mistral-small-latest")
        self.client = Mistral(api_key=self.api_key)
        
        # 默认参数
        self.default_params = {
            "temperature": config.get('temperature', 0.7),
            "max_tokens": config.get('max_tokens', 1024),
            "top_p": config.get('top_p', 0.9)
        }
    
    def generate_response(self, user_input, context=None, **kwargs):
        """
        生成响应
        
        Args:
            user_input (str): 用户输入的文本
            context (dict): 上下文信息，包含历史对话、系统提示等
            **kwargs: 传递给 API 的其他参数
            
        Returns:
            str: 生成的响应文本
        """
        # 构建消息历史
        messages = self._build_messages_from_context(context)
        
        # 添加用户的新消息
        messages.append(ChatMessage(role="user", content=user_input))
        
        # 构建 API 参数
        params = {**self.default_params, **kwargs}
        
        # 调用 Mistral API
        chat_response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=params.get('temperature', self.default_params['temperature']),
            max_tokens=params.get('max_tokens', self.default_params['max_tokens']),
            top_p=params.get('top_p', self.default_params['top_p'])
        )
        
        # 提取并返回响应内容
        return chat_response.choices[0].message.content
    
    def generate_streaming_response(self, user_input, context=None, **kwargs):
        """
        生成流式响应
        
        Args:
            user_input (str): 用户输入的文本
            context (dict): 上下文信息，包含历史对话、系统提示等
            **kwargs: 传递给 API 的其他参数
            
        Returns:
            generator: 生成器，产生响应流
        """
        # 构建消息历史
        messages = self._build_messages_from_context(context)
        
        # 添加用户的新消息
        messages.append(ChatMessage(role="user", content=user_input))
        
        # 构建 API 参数
        params = {**self.default_params, **kwargs}
        
        # 调用 Mistral API 流式接口
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=params.get('temperature', self.default_params['temperature']),
            max_tokens=params.get('max_tokens', self.default_params['max_tokens']),
            top_p=params.get('top_p', self.default_params['top_p']),
            stream=True
        )
        
        # 返回流式响应生成器
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    
    def _build_messages_from_context(self, context):
        """
        从上下文构建消息历史
        
        Args:
            context (dict): 上下文信息，包含历史对话、系统提示等
            
        Returns:
            list: ChatMessage 对象列表
        """
        # 如果没有上下文，返回空消息列表
        if not context:
            return []
        
        messages = []
        
        # 添加系统提示（如果有）
        if context.get('system_prompt'):
            messages.append(ChatMessage(
                role="system",
                content=context.get('system_prompt')
            ))
        
        # 从历史记录中构建消息列表
        for entry in context.get('history', []):
            if 'user' in entry:
                messages.append(ChatMessage(
                    role="user",
                    content=entry['user']
                ))
            elif 'system' in entry:
                messages.append(ChatMessage(
                    role="assistant",
                    content=entry['system']
                ))
        
        return messages
