# Reflection 反思机制方法论

## 背景

Reflection 是 ReAct 循环的第四个环节，在工具执行失败时触发反思，让 Agent 从错误中学习：

```
Thought → Action → Observation → Reflection（失败时）
```

传统 Agent 失败后只是重试或报错，没有"反思为什么失败"的环节。Reflection 通过注入反思提示，引导 Agent 分析失败原因并调整策略。

## 设计思路

### 核心组件

1. **触发条件**：工具执行失败（error 不为空）
2. **反思提示**：引导 Agent 思考失败原因、是否可恢复、替代方案
3. **可见输出**：让用户看到 Reflection 触发（Rich Console）
4. **配置驱动**：可控制是否启用、触发条件

### 实现位置

在 `run_agent.py` 的工具执行路径中：

- **concurrent 路径**：并行工具执行后检查失败
- **sequential 路径**：串行工具执行后检查失败

### 配置驱动

```yaml
agent:
  reflection_enabled: false  # 默认关闭
  reflection_on_failure: true  # 失败时触发
  reflection_on_success: false  # 成功时触发（可选）
  reflection_prompt: ""  # 自定义反思提示
```

## 实现要点

### 1. 配置读取

在 `AIAgent.__init__` 中：

```python
# Reflection 反思配置
self.reflection_enabled = False  # 默认关闭
self.reflection_on_failure = True
self.reflection_on_success = False
self.reflection_prompt = ""

# 从配置文件读取
try:
    _agent_config = _config.get('agent', {})
    self.reflection_enabled = _agent_config.get('reflection_enabled', False)
    self.reflection_on_failure = _agent_config.get('reflection_on_failure', True)
    self.reflection_on_success = _agent_config.get('reflection_on_success', False)
    self.reflection_prompt = _agent_config.get('reflection_prompt', '')
except Exception:
    pass
```

### 2. Reflection 方法

```python
def _reflect_on_tool_failure(
    self,
    tool_name: str,
    error: str,
    iteration: int,
    tool_call: dict = None
) -> str:
    """工具失败时触发反思，返回反思提示.
    
    Args:
        tool_name: 失败的工具名称
        error: 错误信息
        iteration: 当前迭代次数
        tool_call: 工具调用参数（可选）
    
    Returns:
        str: 反思提示，注入到下一轮消息
    """
    if not self._is_reflection_enabled():
        return ""
    
    # 检查是否应该在失败时触发
    if not getattr(self, "reflection_on_failure", True):
        return ""
    
    # 构建反思提示
    reflection_msg = f"""
[REFLECTION TRIGGERED - Tool Failure]

Tool: {tool_name}
Error: {error}
Iteration: {iteration}

工具执行失败。请思考：
1. 失败的可能原因是什么？
2. 是参数问题、环境问题、还是方法不对？
3. 下次遇到相似情境应该如何避免？

Think about:
- Why did this tool fail?
- Is the error recoverable (retry, different parameters)?
- Should I try a different tool or approach?
- Is this a fundamental limitation I should report to the user?
"""
    
    # 可见输出（让用户看到）
    self._print_reflection_trigger(tool_name, error, iteration)
    
    return reflection_msg
```

### 3. 可见输出（关键）

**问题**：CLI 默认 `quiet_mode=True`，普通 `print()` 被抑制。

**解决**：使用 Rich Console 直接输出到终端：

```python
def _print_reflection_trigger(self, tool_name: str, error: str, iteration: int):
    """打印 Reflection 触发消息（绕过 quiet_mode）."""
    try:
        from rich.console import Console
        console = Console()
        console.print(f"\n[bold yellow][REFLECTION TRIGGERED - Tool Failure][/bold yellow]")
        console.print(f"[dim]Tool: {tool_name}[/dim]")
        console.print(f"[dim]Error: {error[:200]}...[/dim]")
        console.print(f"[dim]Iteration: {iteration}[/dim]")
        console.print("[dim]工具执行失败。请思考失败原因...[/dim]\n")
    except ImportError:
        # Fallback: Rich 不可用时用普通 print
        print(f"\n[REFLECTION TRIGGERED - Tool Failure]")
        print(f"Tool: {tool_name}")
        print(f"Error: {error[:200]}...")
        print(f"Iteration: {iteration}")
        print("工具执行失败。请思考失败原因...\n")
```

### 4. 注入位置

**concurrent 路径**（并行工具）：

```python
# 工具执行后
for tool_call, result in tool_results:
    if result.get("error"):
        # 触发 Reflection
        reflection_msg = self._reflect_on_tool_failure(
            tool_name=tool_call["function"]["name"],
            error=result["error"],
            iteration=iteration,
            tool_call=tool_call
        )
        if reflection_msg:
            # 注入到下一轮消息
            messages.append({"role": "user", "content": reflection_msg})
```

**sequential 路径**（串行工具）：

```python
# 工具执行后
if result.get("error"):
    reflection_msg = self._reflect_on_tool_failure(
        tool_name=tool_name,
        error=result["error"],
        iteration=iteration,
        tool_call=tool_call
    )
    if reflection_msg:
        messages.append({"role": "user", "content": reflection_msg})
```

## 配置示例

### 基础配置

```yaml
agent:
  reflection_enabled: true
  reflection_on_failure: true
```

### 成功时也触发

```yaml
agent:
  reflection_enabled: true
  reflection_on_failure: true
  reflection_on_success: true  # 成功时也反思（总结经验）
```

### 自定义提示

```yaml
agent:
  reflection_enabled: true
  reflection_prompt: |
    工具执行失败。请反思：
    1. 为什么失败？
    2. 是否可以重试？
    3. 是否应该换一个方法？
```

## 注意事项

### 1. quiet_mode 陷阱（已解决）

**问题**：CLI 默认 `quiet_mode=True`，`print()` 被抑制，用户看不到 Reflection 触发。

**解决**：使用 Rich Console 直接输出，绕过 quiet_mode。

**教训**：功能实现 ≠ 用户可见，需要实际测试验证。

### 2. 与 ReAct 的关系

Reflection 是 ReAct 的第四环节，但可以独立启用：
- 只启用 Reflection：失败时反思，但没有 Thought/Observation
- 同时启用 ReAct + Reflection：完整的 ReAct 循环

### 3. 迭代次数

记录当前迭代次数，帮助 Agent 了解失败历史：
- 第 1 次失败：可能重试
- 第 3 次失败：应该换方法或报告用户

### 4. 错误信息截断

错误信息可能很长，打印时截断（如前 200 字符），避免刷屏。

## 版本兼容性

如果 Hermes Agent 更新版本，重新实现时：

1. **找到工具执行位置**：concurrent 和 sequential 路径
2. **检查错误**：`if result.get("error")`
3. **触发 Reflection**：调用 `_reflect_on_tool_failure()`
4. **注入消息**：添加到 messages 列表
5. **可见输出**：使用 Rich Console 打印

核心思路不变，只是代码位置可能调整。

## 扩展方向

### 1. 成功时反思

不只是失败，成功时也可以反思（总结经验）：

```yaml
agent:
  reflection_on_success: true
```

### 2. 反思历史记录

记录每次反思的内容，用于后续分析和学习：

```python
self.reflection_history.append({
    "timestamp": datetime.now(),
    "tool": tool_name,
    "error": error,
    "reflection": reflection_content
})
```

### 3. 自定义触发条件

不只是工具失败，也可以在其他场景触发：
- 连续多次相同失败
- 特定工具失败
- 用户请求反思

### 4. 反思结果应用

反思后不只是注入提示，还可以：
- 自动调整参数重试
- 切换到备用工具
- 记录到 backlog

## 测试方法

验证 Reflection 是否工作：

1. 启用配置：`reflection_enabled: true`
2. 故意触发失败：读取不存在的文件
3. 观察终端：应该看到 `[REFLECTION TRIGGERED]` 消息
4. 检查消息：下一轮应该包含反思提示

示例：

```python
read_file(path="/不存在的路径/test.txt")
# 应该看到：
# [REFLECTION TRIGGERED - Tool Failure]
# Tool: read_file
# Error: File not found
# Iteration: 1
```

## 参考资料

- ReAct 论文：[ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.07646)
- Reflection in Agents：https://lilianweng.github.io/posts/2023-06-23-agent/