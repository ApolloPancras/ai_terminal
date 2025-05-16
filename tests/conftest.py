"""
测试配置文件
提供测试所需的共享夹具和配置
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.context_manager import ContextManager
from src.core.llm_client import MistralClient
from src.utils.config_loader import create_default_config


@pytest.fixture
def temp_dir():
    """创建临时目录用于测试"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_config_file(temp_dir):
    """创建临时配置文件"""
    config_path = os.path.join(temp_dir, "config.yaml")
    create_default_config(config_path)
    yield config_path


@pytest.fixture
def mock_context_manager():
    """创建模拟的上下文管理器"""
    context_manager = ContextManager(max_history=10)
    # 设置一些测试数据
    context_manager.current_directory = "/test/directory"
    context_manager.environment_state = {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "HOME": "/home/user",
        "USER": "testuser",
        "SHELL": "/bin/zsh"
    }
    yield context_manager


@pytest.fixture
def mock_llm_client(monkeypatch):
    """创建模拟的 LLM 客户端，避免实际调用 API"""
    class MockMistralClient:
        def __init__(self, config=None):
            self.config = config or {}
            self.model = config.get('model', 'mistral-small-latest') if config else 'mistral-small-latest'
            self.responses = {
                # 对话模式响应
                "什么是容器技术？它与虚拟机有什么区别？": "容器技术是一种轻量级的虚拟化技术，它与传统虚拟机的主要区别在于...",
                "解释一下什么是 RESTful API 以及它的设计原则": "RESTful API 是一种基于 REST 架构风格的应用编程接口...",
                "它与 SVN 相比有什么优势？": "与 SVN 相比，Git 具有以下优势：分布式版本控制、更好的分支管理...",
                
                # 命令模式响应
                "生成一个命令，查找当前目录下所有大于 100MB 且在过去 30 天内修改过的文件": "find . -type f -size +100M -mtime -30",
                "解释命令 ps aux | grep python | awk '{print $2}' | xargs kill -9": "这个命令用于查找并强制终止所有 Python 进程...",
                "优化命令 find . -name \"*.log\" -exec grep \"ERROR\" {} \\;": "find . -name \"*.log\" -exec grep -l \"ERROR\" {} \\;",
                
                # 文档模式响应
                "总结 test_document.txt": "这是一个关于人工智能发展历史的文档，主要讨论了从早期的专家系统到现代深度学习的演变...",
                "分析 test_code.py 的功能和结构": "这个 Python 文件实现了一个简单的 Web 服务器，主要包含以下组件：...",
                "从 test_log.log 中提取所有错误信息并总结常见问题": "日志中主要包含三类错误：连接超时、权限拒绝和内存不足...",
                
                # 默认响应
                "default": "我理解您的问题，这是一个模拟的测试响应。"
            }
        
        def generate_response(self, user_input, context=None, **kwargs):
            # 返回预设的响应或默认响应
            for key, response in self.responses.items():
                if key in user_input:
                    return response
            return self.responses["default"]
        
        def generate_streaming_response(self, user_input, context=None, **kwargs):
            response = self.generate_response(user_input, context, **kwargs)
            # 模拟流式响应
            for word in response.split():
                yield word + " "
    
    # 替换真实的客户端
    monkeypatch.setattr("src.core.llm_client.Mistral", lambda api_key: None)
    
    yield MockMistralClient


@pytest.fixture
def test_files(temp_dir):
    """创建测试文件"""
    # 创建测试文本文件
    text_file = os.path.join(temp_dir, "test_document.txt")
    with open(text_file, "w") as f:
        f.write("""
        人工智能的发展历史
        
        人工智能（AI）的概念可以追溯到20世纪50年代。早期的AI研究主要集中在解决问题和符号推理上。
        20世纪80年代，专家系统成为主流。到了90年代末和21世纪初，机器学习方法开始流行。
        近年来，深度学习的突破带动了AI的快速发展，特别是在图像识别、自然语言处理和游戏等领域。
        未来，AI可能会继续发展，解决更复杂的问题，并与人类社会更深入地融合。
        """)
    
    # 创建测试代码文件
    code_file = os.path.join(temp_dir, "test_code.py")
    with open(code_file, "w") as f:
        f.write("""
        #!/usr/bin/env python3
        \"\"\"
        简单的 Web 服务器示例
        \"\"\"
        
        import http.server
        import socketserver
        
        PORT = 8000
        
        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            \"\"\"自定义请求处理器\"\"\"
            
            def do_GET(self):
                \"\"\"处理 GET 请求\"\"\"
                if self.path == '/hello':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'Hello, World!')
                else:
                    super().do_GET()
        
        def run_server():
            \"\"\"运行服务器\"\"\"
            handler = CustomHandler
            with socketserver.TCPServer(("", PORT), handler) as httpd:
                print(f"Server running at http://localhost:{PORT}")
                httpd.serve_forever()
        
        if __name__ == "__main__":
            run_server()
        """)
    
    # 创建测试日志文件
    log_file = os.path.join(temp_dir, "test_log.log")
    with open(log_file, "w") as f:
        f.write("""
        2023-05-15 10:23:45 INFO  Server started on port 8080
        2023-05-15 10:24:12 ERROR Connection timeout when connecting to database
        2023-05-15 10:25:30 INFO  User 'admin' logged in
        2023-05-15 10:26:45 ERROR Permission denied: cannot write to /var/log/app
        2023-05-15 10:30:22 WARN  High CPU usage detected: 85%
        2023-05-15 10:35:10 ERROR Out of memory: Cannot allocate 256MB
        2023-05-15 10:40:05 INFO  Backup completed successfully
        2023-05-15 10:45:30 ERROR Connection timeout when connecting to API
        2023-05-15 10:50:15 INFO  Server shutdown initiated
        2023-05-15 10:50:20 INFO  Server stopped
        """)
    
    # 创建测试配置文件
    config_file = os.path.join(temp_dir, "test_config.yaml")
    with open(config_file, "w") as f:
        f.write("""
        server:
          host: localhost
          port: 8080
          debug: false
        
        database:
          host: db.example.com
          port: 5432
          user: dbuser
          password: dbpassword
          name: mydb
        
        logging:
          level: info
          file: /var/log/app.log
        """)
    
    # 创建多语言测试文件
    multilingual_file = os.path.join(temp_dir, "multilingual.txt")
    with open(multilingual_file, "w") as f:
        f.write("""
        这是中文内容，用于测试多语言支持。
        English mixed with 中文。
        Это русский текст для проверки поддержки многоязычности.
        これは多言語サポートをテストするための日本語のコンテンツです。
        """)
    
    return {
        "text_file": text_file,
        "code_file": code_file,
        "log_file": log_file,
        "config_file": config_file,
        "multilingual_file": multilingual_file
    }
