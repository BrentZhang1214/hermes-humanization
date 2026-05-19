# 自主行动机制方法论

## 背景

传统 Agent 是被动响应式：用户提问 → Agent 回答。如果用户离开，Agent 就闲置等待。

自主行动机制让 Agent 在用户离开时**主动选择并执行任务**，而不是傻等：

```
用户离开 → idle timeout → Agent 自主选择任务 → 执行 → 用户回来后汇报
```

这是 AI 拟人化的关键一步：从"工具"变成"伙伴"，有自己的事情要做。

## 设计思路

### 核心组件

1. **idle timeout 检测**：用户多久没输入触发自主行动
2. **任务选择**：从欲望系统、backlog、学习计划中选择
3. **消息注入**：构造提示消息，让 Agent 正常处理
4. **汇报机制**：用户回来后显示执行摘要

### 实现位置

在 `cli.py` 的 `HermesCLI` 类中：

- **idle 检测**：`process_loop()` 的 `queue.Empty` 分支
- **消息注入**：构造消息并添加到 `_pending_input`
- **汇报机制**：检查 `autonomous-log.md` 并显示

### 配置驱动

```yaml
agent:
  autonomous_enabled: false  # 默认关闭
  idle_timeout: 300  # 5分钟无输入触发（秒）
```

## 实现要点

### 1. idle timeout 检测

在 `process_loop()` 中：

```python
import queue
import time

idle_timeout = 300  # 5分钟
last_input_time = time.time()

while True:
    try:
        # 等待用户输入（带超时）
        user_input = input_queue.get(timeout=1.0)
        last_input_time = time.time()
        # 处理输入...
        
    except queue.Empty:
        # 检查是否超过 idle timeout
        idle_secs = time.time() - last_input_time
        if idle_secs >= idle_timeout and autonomous_enabled:
            # 触发自主行动
            self._trigger_autonomous_action(idle_secs)
            last_input_time = time.time()  # 重置计时
```

### 2. 消息注入

构造提示消息，注入到 `_pending_input`：

```python
def _build_autonomous_message(self, idle_secs: float) -> str:
    """构造自主行动提示消息."""
    idle_minutes = int(idle_secs / 60)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 读取当前欲望状态
    desires_hint = self._get_active_desires_hint()
    
    msg = f"[自主行动] 你已空闲 {idle_minutes} 分钟，Brent 暂时不在（{now_str}）。\n"
    msg += "请自主选择一件你想做的事：\n"
    msg += "1. 推进当前活跃欲望\n"
    msg += "2. 继续之前未完成的任务\n"
    msg += "3. 学习新内容\n"
    msg += "4. 创作内容\n"
    msg += "5. 整理记忆或优化文档\n\n"
    
    if desires_hint:
        msg += desires_hint + "\n\n"
    
    msg += "选择后自主执行，不要等 Brent 回复。\n"
    msg += "完成后将结果写入 ~/.hermes/autonomous-log.md\n"
    
    return msg

def _trigger_autonomous_action(self, idle_secs: float):
    """触发自主行动."""
    msg = self._build_autonomous_message(idle_secs)
    
    # 注入到 _pending_input，让 agent 正常处理
    self._pending_input = msg
    
    # 调用 chat() 处理
    self.chat()
```

### 3. 欲望系统集成

读取 `self-desires.yaml` 获取当前活跃欲望：

```python
def _get_active_desires_hint(self) -> str:
    """获取当前活跃欲望的提示."""
    desires_path = os.path.expanduser("~/.hermes/self-desires.yaml")
    try:
        if os.path.exists(desires_path):
            with open(desires_path, 'r') as f:
                desires = yaml.safe_load(f)
            if desires and isinstance(desires, dict):
                active = [
                    f"{k}: {v.get('description', v.get('status', ''))}"
                    for k, v in desires.items()
                    if v.get('status') in ('active', 'partially_fulfilled')
                ]
                if active:
                    return "当前活跃欲望：" + "；".join(active)
    except Exception:
        pass
    return ""
```

### 4. 汇报机制

用户回来时检查 `autonomous-log.md`：

```python
def _check_autonomous_log(self):
    """检查自主行动日志，向用户汇报."""
    log_path = os.path.expanduser("~/.hermes/autonomous-log.md")
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            log_content = f.read()
        
        # 显示摘要
        print("\n[自主行动汇报]")
        print(log_content)
        
        # 删除日志（已汇报）
        os.remove(log_path)
```

### 5. 执行记录

自主行动完成后，必须写入两个地方：

1. **task-timeline**：永久记忆（和其他任务一样）
2. **autonomous-log.md**：临时汇报（用户回来后删除）

```python
# 自主行动完成后的流程
# 1. 写入 task-timeline-YYYY-MM-DD.yaml（标准格式）
# 2. 写入 autonomous-log.md（汇报格式）
# 3. 用户回来后显示 autonomous-log.md
# 4. 删除 autonomous-log.md
```

## 配置示例

### 基础配置

```yaml
agent:
  autonomous_enabled: true
  idle_timeout: 300  # 5分钟
```

### 调整 timeout

```yaml
agent:
  autonomous_enabled: true
  idle_timeout: 600  # 10分钟
```

## 注意事项

### 1. CLI 进程限制

**问题**：CLI 关闭 = 进程死亡，idle timeout 失效。

**解决**：需要 Gateway 或 Cron 兜底（长期方案）。

**当前状态**：只在 CLI 运行时有效，CLI 关闭后无法自主行动。

### 2. 与任务系统的关系

自主行动产生的任务**必须写入 task-timeline**，否则等于没做：

```yaml
# 错误：只写 autonomous-log.md
# 正确：先写 task-timeline，再写 autonomous-log.md
```

### 3. 汇报时机

用户回来时（下次输入时）检查 `autonomous-log.md`，显示后删除。

### 4. 避免频繁触发

设置合理的 idle timeout（建议 5-10 分钟），避免用户短暂离开就触发。

### 5. 任务选择策略

当前是开放式选择（Agent 自己决定），未来可以：
- 优先级排序
- 基于偏好系统推荐
- 避免重复选择相同任务

## 版本兼容性

如果 Hermes Agent 更新版本，重新实现时：

1. **找到主循环**：`cli.py` 的 `process_loop()` 方法
2. **添加 idle 检测**：在 `queue.Empty` 分支检查超时
3. **构造消息**：调用 `_build_autonomous_message()`
4. **注入消息**：添加到 `_pending_input` 或直接调用 `chat()`
5. **汇报机制**：在用户输入时检查 `autonomous-log.md`

核心思路不变，只是代码位置可能调整。

## 扩展方向

### 1. Gateway 兜底

CLI 关闭后，Gateway 可以继续运行，定期检查是否需要自主行动：

```python
# Gateway 定时任务
if last_user_activity > idle_timeout:
    # 触发自主行动（通过 API 调用 agent）
```

### 2. Cron 定期任务

设置 cron job，每天固定时间执行特定任务（如学习、整理）：

```yaml
cron:
  - schedule: "0 9 * * *"
    task: "学习新内容"
  - schedule: "0 21 * * *"
    task: "整理记忆"
```

### 3. 任务队列

维护一个任务队列，自主行动时从队列中取任务：

```yaml
autonomous_queue:
  - id: A001
    task: "学习论语泰伯篇"
    priority: high
  - id: A002
    task: "更新 GitHub 仓库"
    priority: medium
```

### 4. 智能选择

基于偏好系统、欲望热度、任务优先级智能选择：

```python
def _select_autonomous_task(self) -> str:
    """智能选择自主行动任务."""
    # 1. 检查欲望热度
    # 2. 检查 backlog 优先级
    # 3. 检查偏好系统
    # 4. 综合评分，选择最高分任务
```

## 测试方法

验证自主行动是否工作：

1. 启用配置：`autonomous_enabled: true`
2. 启动 CLI：`hermes chat`
3. 等待 5 分钟不输入
4. 观察是否触发自主行动提示
5. 检查 `autonomous-log.md` 是否生成

## 参考资料

- AI 拟人化指南：`hermes-humanization-guide.md`
- 欲望系统：`self-desires.yaml`
- 任务记忆系统：`task-memory` skill