# ReAct 循环实现方法论

## 背景

ReAct（Reasoning + Acting）是一种显式的 Agent 决策框架，让思考过程透明化：

```
Thought → Action → Observation → Reflection
```

传统 Agent 的决策过程隐藏在模型内部，用户看不到"为什么选择这个工具"。ReAct 通过显式注入提示，让 Agent 在行动前思考、行动后观察。

## 设计思路

### 核心组件

1. **Thought（思考）**：在 API 调用前注入提示，引导 Agent 思考当前状态、目标、行动选择
2. **Action（行动）**：工具调用（保持原有流程不变）
3. **Observation（观察）**：工具执行后注入结果提示，引导 Agent 观察结果并决定下一步
4. **Reflection（反思）**：失败时触发反思（单独文档描述）

### 实现位置

在 `run_agent.py` 的 `AIAgent` 类中：

- **Thought 注入**：`chat()` 方法中，API 调用前
- **Observation 注入**：工具执行后（concurrent 和 sequential 两条路径）

### 配置驱动

所有功能通过 `config.yaml` 控制，默认关闭：

```yaml
agent:
  react_enabled: false  # 默认关闭
  react_thought_prompt: ""  # 自定义 Thought 提示
  react_observation_prompt: ""  # 自定义 Observation 提示
```

## 实现要点

### 1. 配置读取

在 `AIAgent.__init__` 中读取配置：

```python
# 从 config.yaml 读取 ReAct 设置
try:
    from pathlib import Path as _Path
    import yaml as _yaml
    _config_path = _Path.home() / ".hermes" / "config.yaml"
    if _config_path.exists():
        with open(_config_path, 'r', encoding='utf-8') as _f:
            _config = _yaml.safe_load(_f) or {}
        _agent_config = _config.get('agent', {})
        self.react_enabled = _agent_config.get('react_enabled', False)
        self.react_thought_prompt = _agent_config.get('react_thought_prompt', '')
        self.react_observation_prompt = _agent_config.get('react_observation_prompt', '')
except Exception:
    pass  # 配置读取失败时使用默认值
```

### 2. Thought 注入

在 `chat()` 方法中，构建消息时检查是否启用：

```python
if self._is_react_enabled():
    thought_prompt = self._get_react_thought_prompt()
    # 注入到系统提示或用户消息
```

### 3. Observation 注入

工具执行后，在结果返回前注入：

```python
# concurrent 路径（并行工具）
for tool_call, result in tool_results:
    if self._is_react_enabled():
        observation_prompt = self._get_react_observation_prompt()
        # 注入到下一轮消息

# sequential 路径（串行工具）
if self._is_react_enabled():
    observation_prompt = self._get_react_observation_prompt()
    # 注入到下一轮消息
```

### 4. 辅助方法

```python
def _is_react_enabled(self) -> bool:
    """检查 ReAct 是否启用."""
    return getattr(self, "react_enabled", False)

def _get_react_thought_prompt(self) -> str:
    """获取 Thought 提示模板."""
    return getattr(self, "react_thought_prompt", """
Before taking action, think through:
1. What is the current state?
2. What is the goal?
3. What action should I take?
4. Why this action?
""")

def _get_react_observation_prompt(self) -> str:
    """获取 Observation 提示模板."""
    return getattr(self, "react_observation_prompt", """
Tool execution completed. Observe the result and decide next step.
""")
```

## 配置示例

### 基础配置

```yaml
agent:
  react_enabled: true
```

### 自定义提示

```yaml
agent:
  react_enabled: true
  react_thought_prompt: |
    在行动前，请思考：
    1. 当前状态是什么？
    2. 目标是什么？
    3. 下一步应该采取什么行动？
    4. 为什么选择这个行动？
  react_observation_prompt: |
    工具执行完成。请观察结果并决定下一步。
```

## 注意事项

### 1. 与现有循环的兼容性

ReAct 是在现有循环基础上添加提示，**不改变核心流程**：
- 不改变工具调用机制
- 不改变消息格式
- 只是添加额外的提示内容

### 2. quiet_mode 的影响

Thought 和 Observation 提示注入到消息中，不受 `quiet_mode` 影响。但如果需要打印到终端，需要使用 Rich Console（见 Reflection 文档）。

### 3. 性能考虑

每次 API 调用前注入 Thought 提示会增加 token 消耗。建议：
- 提示模板保持简洁
- 只在需要透明决策的场景启用

### 4. 与 Reflection 的配合

ReAct 的 Reflection 环节是单独实现的（见 `reflection-mechanism.md`），两者可以独立启用：
- 只启用 ReAct：Thought + Action + Observation
- 同时启用：Thought + Action + Observation + Reflection（失败时）

## 版本兼容性

如果 Hermes Agent 更新版本，重新实现时：

1. **找到消息构建位置**：`chat()` 方法中构建 messages 的地方
2. **找到工具执行位置**：concurrent 和 sequential 两条路径
3. **添加配置读取**：在 `__init__` 中读取 config.yaml
4. **注入提示**：在合适位置添加 Thought 和 Observation 提示

核心思路不变，只是代码位置可能调整。

## 扩展方向

### 1. 提取 ReAct 组件

从响应内容中提取 Thought/Action/Observation，用于可视化或日志：

```python
def _extract_react_components(self, content: str) -> dict:
    """从响应内容中提取 ReAct 组件."""
    # 提取 thinking 标签中的内容
    # 提取 tool_calls 作为 Action
    # 提取工具结果作为 Observation
```

### 2. ReAct 日志

记录每次 ReAct 循环的 Thought/Action/Observation，用于调试和分析。

### 3. 自定义 Reflection 触发条件

不只是失败时触发，也可以在成功时触发（总结经验）。

## 参考资料

- ReAct 论文：[ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.07646)
- LangChain ReAct 实现：https://python.langchain.com/docs/modules/agents/agent_types/react