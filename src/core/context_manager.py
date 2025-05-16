#!/usr/bin/env python3
"""
上下文管理器模块
负责管理和维护对话历史、用户环境信息、命令历史等上下文数据
"""

import os
import json
from datetime import datetime
from collections import Counter
from pathlib import Path


class ContextManager:
    """上下文管理器，负责维护和更新系统的上下文信息"""

    def __init__(self, max_history=20):
        """
        初始化上下文管理器

        Args:
            max_history (int): 保留的最大历史记录条数
        """
        self.conversation_history = []
        self.environment_state = {}
        self.current_directory = None
        self.recent_commands = []
        self.document_context = {}
        self.max_history = max_history

        # 创建上下文存储目录
        self.context_dir = Path(os.path.expanduser("~/.ai_terminal"))
        self.context_dir.mkdir(exist_ok=True)

        # 加载保存的上下文（如果存在）
        self._load_context_from_disk()

    def update_context(self, user_input, system_response=None, mode=None):
        """
        更新会话上下文

        Args:
            user_input (str): 用户输入
            system_response (str): 系统响应
            mode (str): 操作模式（对话、命令、文档）
        """
        # 更新会话历史
        entry = {
            "user": user_input,
            "timestamp": datetime.now().isoformat(),
            "mode": mode or "conversation"
        }

        if system_response:
            entry["system"] = system_response

        self.conversation_history.append(entry)

        # 保持最近的 N 轮对话
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def update_environment(self, env_vars=None, cwd=None, command=None):
        """
        更新环境状态

        Args:
            env_vars (dict): 环境变量
            cwd (str): 当前工作目录
            command (str): 执行的命令
        """
        if env_vars:
            self.environment_state.update(env_vars)

        if cwd:
            self.current_directory = cwd

        if command:
            self.recent_commands.append({
                "command": command,
                "timestamp": datetime.now().isoformat(),
                "cwd": self.current_directory
            })

            # 保持最近的命令记录
            if len(self.recent_commands) > 20:  # 保留20条命令记录
                self.recent_commands = self.recent_commands[-20:]

    def add_document_context(self, file_path, summary=None, analysis=None):
        """
        添加文档上下文

        Args:
            file_path (str): 文件路径
            summary (str): 文件摘要
            analysis (str): 文件分析结果
        """
        self.document_context[file_path] = {
            "last_accessed": datetime.now().isoformat(),
            "summary": summary,
            "analysis": analysis
        }

    def build_context_for_mistral(self, mode="conversation"):
        """
        为 Mistral API 构建上下文

        Args:
            mode (str): 操作模式（对话、命令、文档）

        Returns:
            dict: 包含上下文信息的字典
        """
        from src.utils.config_manager import MistralConfigManager

        context = {
            "system_prompt": MistralConfigManager.MODES[mode]["system_prompt"],
            "history": self._get_relevant_history(mode),
            "env_info": {
                "cwd": self.current_directory,
                "recent_commands": self.recent_commands[-5:] if self.recent_commands else []
            }
        }

        # 根据不同模式增加额外上下文
        if mode == "command" and self.recent_commands:
            # 对命令模式，增加最近使用的命令作为上下文
            context["command_patterns"] = self._extract_command_patterns()

        elif mode == "document" and self.document_context:
            # 对文档模式，增加最近访问的文档信息
            context["recent_documents"] = self._get_recent_documents(3)

        return context

    def save_context_to_disk(self):
        """将上下文保存到磁盘"""
        context_file = self.context_dir / "context.json"

        # 准备要保存的数据
        data = {
            "conversation_history": self.conversation_history,
            "environment_state": self.environment_state,
            "current_directory": self.current_directory,
            "recent_commands": self.recent_commands,
            "document_context": self.document_context
        }

        # 保存到文件
        with open(context_file, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_context_from_disk(self):
        """从磁盘加载上下文"""
        context_file = self.context_dir / "context.json"

        if context_file.exists():
            try:
                with open(context_file, "r") as f:
                    data = json.load(f)

                self.conversation_history = data.get("conversation_history", [])
                self.environment_state = data.get("environment_state", {})
                self.current_directory = data.get("current_directory")
                self.recent_commands = data.get("recent_commands", [])
                self.document_context = data.get("document_context", {})
            except Exception as e:
                print(f"加载上下文失败: {str(e)}")

    def _get_relevant_history(self, current_mode, max_entries=10):
        """
        获取与当前模式相关的历史记录

        Args:
            current_mode (str): 当前操作模式
            max_entries (int): 最大返回条数

        Returns:
            list: 相关历史记录
        """
        # 提取所有历史记录中与当前模式匹配的条目
        relevant = [
            entry for entry in self.conversation_history
            if entry.get("mode") == current_mode
        ]

        # 如果相关历史太少，也包含一些通用对话
        if len(relevant) < max_entries // 2:
            general = [
                entry for entry in self.conversation_history
                if entry.get("mode") != current_mode
            ]
            # 合并并保持时间顺序
            all_entries = sorted(
                relevant + general,
                key=lambda x: x.get("timestamp", "")
            )
            return all_entries[-max_entries:]

        # 返回最近的相关历史
        return relevant[-max_entries:]

    def _extract_command_patterns(self):
        """
        分析用户命令模式和偏好

        Returns:
            dict: 命令模式信息
        """
        # 实际实现会更复杂，这里简化处理
        commands = [cmd["command"] for cmd in self.recent_commands]

        patterns = {
            "frequent_commands": Counter([cmd.split()[0] for cmd in commands if cmd]).most_common(3),
            "command_complexity": self._estimate_complexity(commands),
            "preferred_tools": self._extract_tools(commands)
        }

        return patterns

    def _estimate_complexity(self, commands):
        """
        估计命令复杂度

        Args:
            commands (list): 命令列表

        Returns:
            str: 复杂度级别 (simple, moderate, complex)
        """
        if not commands:
            return "simple"

        # 简单评估逻辑
        avg_length = sum(len(cmd.split()) for cmd in commands) / max(len(commands), 1)
        pipe_count = sum("|" in cmd for cmd in commands)

        if avg_length > 5 or pipe_count > len(commands) / 3:
            return "complex"
        elif avg_length > 3 or pipe_count > 0:
            return "moderate"
        else:
            return "simple"

    def _extract_tools(self, commands):
        """
        提取用户常用的工具

        Args:
            commands (list): 命令列表

        Returns:
            list: 常用工具列表
        """
        if not commands:
            return []

        # 提取所有命令的第一个词（通常是工具名）
        tools = [cmd.split()[0] for cmd in commands if cmd and cmd.strip()]
        return [tool for tool, _ in Counter(tools).most_common(5)]

    def _get_recent_documents(self, count=3):
        """
        获取最近处理的文档信息

        Args:
            count (int): 返回的文档数量

        Returns:
            dict: 最近文档信息
        """
        # 按最后访问时间排序
        recent = sorted(
            self.document_context.items(),
            key=lambda x: x[1].get("last_accessed", ""),
            reverse=True
        )

        return dict(recent[:count])
