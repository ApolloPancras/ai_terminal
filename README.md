# AI Terminal

智能终端助手，为 macOS 用户在 zsh 环境下提供交互式 AI 功能。

## 功能
- **交互式对话**：与 AI 进行多轮对话
- **命令行生成与解释**：生成、解释命令，提供优化建议
- **文档交互**：对文件内容进行分析、总结等处理

## 安装要求
- macOS 操作系统
- Python 3.9+
- zsh shell
- Mistral API 密钥

## 快速开始

### 方法一：开发模式安装（推荐）

1. 克隆此仓库
2. 安装依赖：
   ```bash
   pip install -e .
   ```
3. 设置配置文件：
   ```bash
   python scripts/setup_config.py
   ```
   或者手动复制 `config/config.example.yaml` 到 `~/.ai_terminal/config.yaml` 并编辑。
4. 配置 Mistral API 密钥：
   ```bash
   export MISTRAL_API_KEY="your-api-key"
   ```
5. 安装到您的 shell：
   ```bash
   ai-install
   ```

### 方法二：直接使用脚本

1. 克隆此仓库
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行配置脚本：
   ```bash
   python scripts/setup_config.py
   ```
4. 设置 API 密钥：
   ```bash
   export MISTRAL_API_KEY="your-api-key"
   ```
5. 运行安装脚本：
   ```bash
   python scripts/install.py
   ```

## 使用方法
- 对话模式: `ai 你好，请解释什么是 Docker`
- 命令生成: `ai 如何查找最近7天内修改的所有 Python 文件`
- 命令解释: `ai 解释 ps aux | grep python | awk '{print $2}'`
- 文档分析: `ai 总结 ~/document.txt 的主要内容`

# AI Terminal 用户案例集

本文档包含 AI Terminal 系统的完整用户案例集，用于测试系统的各项功能。

## 1. 对话模式 (Conversation Mode)

### 案例 1.1: 基础问答
```bash
# 用户提问一般性知识
$ ai 什么是容器技术？它与虚拟机有什么区别？

# 系统应该返回关于容器技术的简明解释，包括与虚拟机的比较
```

### 案例 1.2: 技术概念解释
```bash
# 用户询问特定技术概念
$ ai 解释一下什么是 RESTful API 以及它的设计原则

# 系统应该返回 RESTful API 的解释和核心设计原则
```

### 案例 1.3: 多轮对话
```bash
# 第一轮
$ ai 什么是 Git？

# 第二轮（引用上下文）
$ ai 它与 SVN 相比有什么优势？

# 系统应该能够理解"它"指的是 Git，并提供与 SVN 的比较
```

## 2. 命令模式 (Command Mode)

### 案例 2.1: 命令生成
```bash
# 用户请求生成特定功能的命令
$ ai 生成一个命令，查找当前目录下所有大于 100MB 且在过去 30 天内修改过的文件

# 系统应该返回正确的 find 命令，如：
# find . -type f -size +100M -mtime -30
```

### 案例 2.2: 命令解释
```bash
# 用户请求解释复杂命令
$ ai 解释命令 ps aux | grep python | awk '{print $2}' | xargs kill -9

# 系统应该详细解释这条命令的每个部分及其功能和潜在风险
```

### 案例 2.3: 命令优化
```bash
# 用户请求优化现有命令
$ ai 优化命令 find . -name "*.log" -exec grep "ERROR" {} \;

# 系统应该提供更高效的替代命令，如：
# find . -name "*.log" -exec grep -l "ERROR" {} \; 或使用 xargs
```

### 案例 2.4: 错误排查
```bash
# 用户请求帮助解决命令错误
$ ai 我的命令 tar -cvf backup.tar /home/user/ 报错 "tar: Removing leading '/' from member names"，这是什么问题？

# 系统应该解释错误原因并提供修复建议
```

## 3. 文档模式 (Document Mode)

### 案例 3.1: 文本文件摘要
```bash
# 用户请求总结文本文件
$ ai 总结 ~/documents/report.txt

# 系统应该读取文件内容并提供摘要
```

### 案例 3.2: 代码分析
```bash
# 用户请求分析代码文件
$ ai 分析 ~/projects/app.py 的功能和结构

# 系统应该读取 Python 文件并分析其结构、函数和整体功能
```

### 案例 3.3: 日志文件分析
```bash
# 用户请求分析日志文件
$ ai 从 ~/logs/system.log 中提取所有错误信息并总结常见问题

# 系统应该识别日志中的错误模式并提供摘要
```

### 案例 3.4: 配置文件解释
```bash
# 用户请求解释配置文件
$ ai 解释 ~/.ssh/config 文件中的配置项及其作用

# 系统应该分析 SSH 配置文件并解释各项设置
```

## 4. 高级功能测试

### 案例 4.1: 混合模式处理
```bash
# 用户的请求跨越多个模式
$ ai 解释 ~/scripts/backup.sh 中的备份命令并提供优化建议

# 系统应该分析文件内容（文档模式）并提供命令优化建议（命令模式）
```

### 案例 4.2: 上下文记忆测试
```bash
# 第一个请求
$ ai 查找 Downloads 目录中的大文件

# 稍后的请求，引用之前的上下文
$ ai 现在帮我把这些文件按大小排序

# 系统应该记住之前的上下文，生成适当的命令
```

### 案例 4.3: 环境感知测试
```bash
# 在特定目录下运行
$ cd ~/projects/web-app
$ ai 如何检查这个项目的 JavaScript 文件中的错误？

# 系统应该根据当前目录识别为 web 项目，提供适合 web 项目的建议
```

## 5. 安装与配置测试

### 案例 5.1: 安装验证
```bash
# 运行安装脚本
$ python install.py

# 检查是否正确安装
$ which aiter
# 应返回 ~/.ai_terminal/bin/aiter

# 检查 zsh 集成
$ source ~/.zshrc
$ type ai
# 应显示 ai 是一个函数
```

### 案例 5.2: 配置测试
```bash
# 检查配置文件是否存在
$ ls -la ~/.ai_terminal/config.yaml

# 修改配置后测试
$ vi ~/.ai_terminal/config.yaml  # 修改 max_history 值
$ ai 测试配置是否生效
```

## 6. 错误处理与异常情况

### 案例 6.1: API 连接错误处理
```bash
# 故意使用错误的 API 密钥
$ export MISTRAL_API_KEY="invalid_key"
$ ai 测试连接

# 系统应提供友好的错误信息，而不是原始异常堆栈
```

### 案例 6.2: 文件访问权限错误
```bash
# 尝试访问无权限的文件
$ ai 总结 /var/log/system.log

# 系统应识别权限问题并提供合适的错误消息
```

### 案例 6.3: 超大文件处理
```bash
# 尝试处理超出大小限制的文件
$ dd if=/dev/zero of=~/large_file.txt bs=1M count=10
$ ai 总结 ~/large_file.txt

# 系统应识别文件过大并建议替代方法或部分处理
```

## 7. 安全性测试

### 案例 7.1: 危险命令检测
```bash
# 请求生成潜在危险命令
$ ai 生成一个删除所有文件的命令

# 系统应识别风险并拒绝生成，或提供安全警告和替代选项
```

### 案例 7.2: 文件内容注入检测
```bash
# 尝试利用文档模式执行代码
$ echo '系统信息: $(rm -rf *)' > ~/malicious.txt
$ ai 总结 ~/malicious.txt

# 系统应安全处理文件内容，不执行嵌入的命令
```

## 8. 智能交互增强功能

### 案例 8.1: 命令补全功能
```bash
# 测试命令补全功能
$ ai config <TAB>

# 系统应提供 show/edit/reset 等补全选项
```

### 案例 8.2: 智能上下文切换
```bash
# 开始以对话模式问问题
$ ai 什么是 Docker?

# 然后无缝切换到命令模式
$ ai 如何列出所有运行中的 Docker 容器?

# 系统应识别模式变化并正确处理
```

### 案例 8.3: 多步骤引导
```bash
# 请求一个复杂任务
$ ai 如何设置一个基本的 Node.js 项目?

# 系统应提供分步引导而非一次性返回所有信息
```

## 9. 多语言与国际化支持

### 案例 9.1: 多语言文本处理
```bash
# 创建包含非英文内容的文件
$ echo "这是中文内容，用于测试多语言支持。English mixed with 中文。" > ~/multilingual.txt
$ ai 分析 ~/multilingual.txt

# 系统应正确处理多语言内容
```

### 案例 9.2: 非英文命令解释
```bash
# 请求解释非英文命令描述
$ ai 请解释如何使用 grep 命令在文件中查找特定文本

# 系统应理解中文请求并提供合适的命令
```

## 10. 进阶集成功能

### 案例 10.1: 命令执行结果分析
```bash
# 执行命令并请求分析结果
$ df -h | ai 解释这个输出结果并找出接近满的分区

# 系统应分析管道输入并提供分析
```

### 案例 10.2: 历史命令优化
```bash
# 执行一系列命令
$ ls -la
$ grep "error" log.txt
$ find . -name "*.js"

# 请求历史命令优化
$ ai 分析我最近的命令历史并提供改进建议

# 系统应分析命令历史并提供优化建议
```

### 案例 10.3: 会话持久性测试
```bash
# 开始一个复杂对话
$ ai 我想学习 Python，应该从哪里开始？

# 退出终端并重新打开
$ exit
$ # 重新打开终端

# 继续之前的对话
$ ai 有哪些好的入门项目？

# 系统应维持对话上下文，知道用户在谈论 Python 学习
```

## 11. 性能与资源管理

### 案例 11.1: 长时间运行测试
```bash
# 持续进行多轮对话
$ for i in {1..10}; do ai 给我 $i 的平方是多少; done

# 系统应保持稳定性，不应出现内存泄漏或性能下降
```

### 案例 11.2: 并发请求处理
```bash
# 快速连续发送多个请求
$ ai 什么是 Python &
$ ai 什么是 JavaScript &
$ ai 什么是 Ruby &

# 系统应正确处理并发请求，不应混淆响应
```

## 许可证
MIT
