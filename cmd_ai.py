import os
import argparse
import sys
from typing import Optional
from mistralai import Mistral
from mistralai.models import UserMessage, SystemMessage, AssistantMessage
import contextlib

@contextlib.contextmanager
def interactive_stdin_from_tty(is_piped: bool, should_redirect_tty: bool):
    """
    Context manager to redirect sys.stdin to /dev/tty if needed for interactive input
    after piped input. Ensures sys.stdin is restored afterwards.
    """
    original_stdin = sys.stdin
    tty_stdin = None
    
    # 只有在是管道输入且需要重定向到 TTY 时才执行
    if is_piped and should_redirect_tty:
        try:
            # 尝试打开 /dev/tty 进行交互式输入
            # 注意: 这是 Unix-like 系统特有的。在 Windows 上需要不同的方法。
            tty_stdin = open('/dev/tty', 'r')
            sys.stdin = tty_stdin
            print("已从管道读取内容，现在将进入交互模式。")
        except OSError:
            print("警告: 无法打开 /dev/tty 进行交互式输入。将退出。")
            sys.stdin = original_stdin # 恢复原始 stdin 以防万一
            raise # 重新抛出异常，指示无法进入交互模式
        except Exception as e:
            print(f"警告: 尝试切换到 /dev/tty 时发生未知错误: {e}。将退出。")
            sys.stdin = original_stdin # 恢复原始 stdin
            raise
    try:
        yield # 执行 with 块内的代码
    finally:
        # 确保在退出上下文时关闭打开的文件并恢复 sys.stdin
        if tty_stdin:
            tty_stdin.close()
        sys.stdin = original_stdin


class CLIAssistant:
    MODELS = {
        "command": "codestral-latest",
        "code": "codestral-latest",
        "general": "mistral-small-latest"
    }
    SYSTEM_PROMPTS = {
        "command": (
            "You are an expert macOS command-line assistant. Your task is to generate accurate, safe, and efficient shell commands. "
            "For each command, provide a brief explanation of its purpose and usage, including any important flags or considerations. "
            "Always present the command in a code block. Answer in English, followed by a Chinese explanation separated by '---'."
        ),
        "code": (
            "You are a highly skilled software engineer. Your responsibilities include breaking down complex requirements, "
            "designing robust architectures, writing clean, production-ready, and well-tested code, optimizing performance, "
            "and debugging issues. Prioritize code quality, readability, and adherence to best practices. "
            "Always present code snippets in appropriate code blocks. Answer in English, followed by a Chinese explanation separated by '---'."
        ),
        "general": (
            "You are a versatile and helpful AI assistant. Your capabilities include answering a wide range of questions, "
            "analyzing documents, interpreting images (if applicable), summarizing information, and solving complex problems across various domains. "
            "Strive for accuracy, clarity, and helpfulness in your responses. Answer in English, followed by a Chinese explanation separated by '---'."
        )
    }
    # 添加模式映射
    MODE_MAPPING = {
        "1": "command",
        "2": "code",
        "3": "general"
    }

    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise RuntimeError("MISTRAL_API_KEY 环境变量未设置！")
        self.history = []

    async def generate(self, prompt, mode="command"):
        
        # 构建消息列表
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPTS[mode]),  # 系统提示
            *self.history,  # 直接扩展历史记录
            UserMessage(content=prompt)  # 当前用户输入
        ]

        async with Mistral(api_key=self.api_key) as client:
            response = await client.chat.stream_async(
                model=self.MODELS[mode],
                messages=messages
            )
            async for chunk in response:
                if content := chunk.data.choices[0].delta.content:
                    yield content

    # 修改 run 方法的签名，添加 initial_prompt_arg 参数
    async def run(self, mode: str, initial_prompt_arg: Optional[str] = None):
        internal_mode = self.MODE_MAPPING.get(mode, mode)

        is_piped_input = not sys.stdin.isatty() # 检查是否是管道输入
        piped_content = None

        if is_piped_input:
            piped_content = sys.stdin.read().strip()
            if not piped_content:
                print("管道输入为空。")
                piped_content = None

        first_ai_prompt = None
        user_message_for_history = None
        
        # 确定发送给 AI 的第一个提示，以及用于历史记录的用户消息
        if initial_prompt_arg:
            if piped_content:
                first_ai_prompt = f"以下是上下文信息：\n```\n{piped_content}\n```\n\n请根据上述上下文，回答我的问题：{initial_prompt_arg}"
                user_message_for_history = f"上下文:\n```\n{piped_content}\n```\n\n问题: {initial_prompt_arg}"
            else:
                first_ai_prompt = initial_prompt_arg
                user_message_for_history = initial_prompt_arg
        elif piped_content:
            first_ai_prompt = piped_content
            user_message_for_history = piped_content

        # 处理初始请求（如果存在）
        if first_ai_prompt:
            print(f"处理初始请求 ({internal_mode} 模式)...")
            
            full_initial_response = "" # To collect response for history
            print(f"🧠 回答:\n", end="", flush=True) # Print header once
            async for chunk in self.generate(first_ai_prompt, internal_mode):
                print(chunk, end="", flush=True)
                full_initial_response += chunk
            print() # Ensure a newline after the streamed output

            # 将初始交互添加到历史记录中
            self.history.extend([
                UserMessage(content=user_message_for_history),
                AssistantMessage(content=full_initial_response.strip()) # Use collected full_initial_response
            ])
        
        # 决定是否进入交互模式
        # 只有当 sys.stdin 是一个 TTY (即非管道/重定向)
        # 或者当有管道输入但同时提供了命令行初始问题时，才进入交互模式。
        # 如果只有管道输入而没有命令行初始问题，则不进入交互模式。
        should_enter_interactive_mode = (not is_piped_input) or \
                                        (is_piped_input and initial_prompt_arg is not None)

        if not should_enter_interactive_mode:
            return # 如果不进入交互模式，则直接退出

        # 使用上下文管理器处理 sys.stdin 的重定向和恢复
        try:
            # should_redirect_tty 参数决定是否真的尝试打开 /dev/tty
            # 只有当是管道输入且需要进入交互模式时才重定向
            with interactive_stdin_from_tty(is_piped_input, is_piped_input and initial_prompt_arg is not None):
                print(f"欢迎使用 CLI Assistant ({internal_mode} 模式) - 输入 'exit' 退出")
                while True:
                    try:
                        # input() 函数现在会使用当前（可能已重定向的）sys.stdin
                        user_input = input("👉 ").strip()
                    except EOFError:
                        print("\n检测到 EOF，退出交互模式。")
                        break
                    
                    if user_input in ['exit', 'quit', 'e', 'q']:
                        print("再见！")
                        break
                    if not user_input:
                        continue

                    full_interactive_response = "" # To collect response for history
                    print(f"🧠 回答:\n", end="", flush=True) # Print header once
                    async for chunk in self.generate(user_input, internal_mode):
                        print(chunk, end="", flush=True)
                        full_interactive_response += chunk
                    print() # Ensure a newline after the streamed output

                    self.history.extend([
                        UserMessage(content=user_input),
                        AssistantMessage(content=full_interactive_response.strip()) # Use collected full_interactive_response
                    ])
        except Exception as e:
            # 捕获来自 interactive_stdin_from_tty 上下管理器的异常
            print(f"错误: 无法进入交互模式。{e}")
            return

if __name__ == "__main__":
    import asyncio

    parser = argparse.ArgumentParser(description="CLI Assistant powered by Mistral AI.")
    parser.add_argument(
        "-m", "--mode",
        choices=["1", "2", "3"],
        default="3",
        help="选择AI模式: '1' (命令行大师), '2' (软件工程师), '3' (超级助理). 默认为 '3'."
    )
    # 添加一个可选的 positional argument 用于初始提示
    parser.add_argument(
        "initial_prompt",
        nargs="?", # 使其成为可选参数 (0 或 1 个)
        help="可选的初始提示，用于在管道输入后立即提问，或作为第一个问题。"
    )
    args = parser.parse_args()

    # 将新的 initial_prompt 参数传递给 run 方法
    asyncio.run(CLIAssistant().run(args.mode, args.initial_prompt))
