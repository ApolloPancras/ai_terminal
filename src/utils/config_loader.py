#!/usr/bin/env python3
"""
配置加载器模块
负责加载、解析和验证系统配置
"""

import os
import yaml
from pathlib import Path


def load_config(config_path=None):
    """
    加载配置文件
    
    Args:
        config_path (str, optional): 配置文件路径
        
    Returns:
        dict: 配置参数
    """
    # 默认配置路径
    if not config_path:
        config_path = os.path.expanduser("~/.ai_terminal/config.yaml")
    
    # 如果配置文件不存在，创建默认配置
    config_file = Path(config_path)
    if not config_file.exists():
        create_default_config(config_path)
    
    # 读取配置文件
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # 处理环境变量
    process_env_vars(config)
    
    return config


def create_default_config(config_path):
    """
    创建默认配置文件
    
    Args:
        config_path (str): 配置文件路径
    """
    # 确保目录存在
    config_dir = os.path.dirname(config_path)
    os.makedirs(config_dir, exist_ok=True)
    
    # 默认配置
    default_config = {
        "api": {
            "provider": "mistral",
            "model": "mistral-small-latest",
            "api_key": "${MISTRAL_API_KEY}"
        },
        "mistral": {
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": 0.9
        },
        "terminal": {
            "command_prefix": "ai",
            "max_history": 20
        },
        "ui": {
            "enable_suggestions": True,
            "enable_highlighting": True,
            "max_suggestions": 3
        }
    }
    
    # 写入配置文件
    with open(config_path, "w") as f:
        yaml.dump(default_config, f, default_flow_style=False)


def process_env_vars(config):
    """
    处理配置中的环境变量引用
    
    Args:
        config (dict): 配置参数
    """
    if isinstance(config, dict):
        for key, value in config.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                config[key] = os.environ.get(env_var, "")
            elif isinstance(value, (dict, list)):
                process_env_vars(value)
    elif isinstance(config, list):
        for i, item in enumerate(config):
            if isinstance(item, (dict, list)):
                process_env_vars(item)


def validate_config(config):
    """
    验证配置是否有效
    
    Args:
        config (dict): 配置参数
        
    Returns:
        bool: 配置是否有效
        list: 错误信息列表
    """
    errors = []
    
    # 检查必要的配置项
    if "api" not in config:
        errors.append("缺少 API 配置")
    elif "provider" not in config["api"]:
        errors.append("缺少 API 提供商配置")
    elif "model" not in config["api"]:
        errors.append("缺少模型配置")
    
    # 检查 API 密钥
    if "api" in config and "api_key" in config["api"] and not config["api"]["api_key"]:
        errors.append("缺少 API 密钥")
    
    # 返回验证结果
    return len(errors) == 0, errors
