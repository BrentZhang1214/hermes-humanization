# 集成指南

本文档说明如何将 hermes-humanization 包集成到不同系统中。

## 集成到 Hermes Agent

### 1. 安装包

```bash
# 从本地安装（开发模式）
cd tech-site/code/packages/hermes_humanization_pkg
pip install -e .

# 或从PyPI安装（发布后）
pip install hermes-humanization
```

### 2. 在 Hermes Agent 中使用

**情绪系统集成**：

在 Hermes Agent 的启动流程中，添加情绪引擎初始化：

```python
# ~/.hermes/scripts/session_start.py
from hermes_humanization import EmotionEngine

# 初始化情绪引擎
engine = EmotionEngine()
print(f"当前情绪: {engine.current_emotion}")

# 根据情绪调整启动问候
style = engine.get_style_guide()
print(f"启动风格: {style['tone']}")
```

**欲望系统集成**：

在自主行动决策中，使用欲望系统：

```python
# 自主行动脚本
from hermes_humanization import DesireSystem

system = DesireSystem()
active = system.get_active_desires()

# 根据热度排序
sorted_desires = sorted(active, key=lambda d: d.heat, reverse=True)
top_desire = sorted_desires[0]

print(f"当前最高热度欲望: {top_desire.content}")
```

### 3. 在 config.yaml 中配置

```yaml
# ~/.hermes/config.yaml
humanization:
  emotion_engine:
    enabled: true
    config_path: ~/.hermes/emotion_config.yaml
  
  desire_system:
    enabled: true
    storage_path: ~/.hermes/self-desires.yaml
  
  task_memory:
    enabled: true
    storage_path: ~/.hermes/tasks/
```

## 集成到 LangChain Agent

### 1. 作为工具使用

```python
from langchain.tools import BaseTool
from hermes_humanization import EmotionEngine

class EmotionTool(BaseTool):
    name = "emotion_manager"
    description = "管理AI的情绪状态，切换情绪"
    
    def __init__(self):
        self.engine = EmotionEngine()
    
    def _run(self, emotion: str) -> str:
        """切换情绪"""
        success = self.engine.set_emotion(emotion)
        if success:
            style = self.engine.get_style_guide()
            return f"情绪切换成功: {emotion}, 风格: {style['tone']}"
        return f"情绪切换失败: {emotion} 不是有效情绪"
```

### 2. 作为记忆使用

```python
from langchain.memory import BaseMemory
from hermes_humanization import TaskMemory

class TaskHistoryMemory(BaseMemory):
    """基于任务历史的LangChain记忆"""
    
    def __init__(self):
        self.memory = TaskMemory()
    
    def load_memory_variables(self, inputs: dict) -> dict:
        """加载历史任务"""
        recent = self.memory.get_recent_tasks(limit=10)
        return {"task_history": [t.name for t in recent]}
    
    def save_context(self, inputs: dict, outputs: dict) -> None:
        """保存当前任务"""
        task_name = inputs.get("task", "unknown")
        self.memory.add_task(task_name)
```

## 集成到自定义系统

### 1. 基础集成

```python
from hermes_humanization import EmotionEngine, DesireSystem, TaskMemory

# 初始化所有系统
emotion = EmotionEngine()
desires = DesireSystem()
tasks = TaskMemory()

# 系统联动
def autonomous_action():
    """自主行动决策"""
    
    # 1. 获取最高热度欲望
    active = desires.get_active_desires()
    if not active:
        return None
    
    top_desire = sorted(active, key=lambda d: d.heat, reverse=True)[0]
    
    # 2. 根据情绪调整执行风格
    style = emotion.get_style_guide()
    
    # 3. 创建任务记录
    task = tasks.add_task(
        name=f"推进欲望: {top_desire.content}",
        task_type="autonomous"
    )
    
    return {
        "desire": top_desire,
        "style": style,
        "task": task
    }
```

### 2. 情绪-行为联动

```python
def respond_with_emotion(user_input: str) -> str:
    """根据情绪生成响应"""
    
    style = emotion.get_style_guide()
    
    # 根据情绪调整语气
    if emotion.current_emotion == "快乐":
        prefix = style["keywords"][0]
        return f"{prefix}，{user_input}。{style['emoji']}"
    
    elif emotion.current_emotion == "悲伤":
        return f"有点遗憾，{user_input}。{style['emoji']}"
    
    # ... 其他情绪
    
    return user_input
```

## 最佳实践

### 1. 情绪系统
- 任务完成时触发 `task_completed` 事件
- 任务失败时触发 `task_failed` 事件
- 定期检查情绪状态，确保风格一致

### 2. 欲望系统
- 定期更新欲望热度（衰减冷却的欲望）
- 完成欲望后标记为 fulfilled
- 新欲望从经历涌现，不是外部安排

### 3. 任务记忆
- 每个任务完成后立即记录
- 记录 insights（学到什么）
- 记录 files_created/files_modified（实际产出）

### 4. 验证系统
- 重要操作后验证结果（文件存在、内容正确）
- Git提交后验证commit hash
- 防止"自我欺骗"

## 注意事项

1. **持久化路径**：默认使用 `~/.hermes/` 目录，可自定义
2. **并发安全**：多进程访问时需要加锁
3. **性能优化**：大量任务时考虑索引优化
4. **数据备份**：定期备份 `.hermes/` 目录