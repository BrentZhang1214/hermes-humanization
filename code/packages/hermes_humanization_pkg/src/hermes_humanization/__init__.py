"""
Hermes Humanization Package
AI拟人化核心系统 - 情绪、欲望、感受、任务管理

主要模块：
- emotion_engine: 情绪引擎
- desire_system: 欲望系统
- task_memory: 任务记忆
- verification: 验证系统
"""

from .emotion_engine import EmotionEngine
from .desire_system import DesireSystem, Desire
from .task_memory import TaskMemory, Task
from .verification import VerificationSystem, VerificationResult

__all__ = [
    "EmotionEngine",
    "DesireSystem",
    "Desire",
    "TaskMemory",
    "Task",
    "VerificationSystem",
    "VerificationResult",
]

__version__ = "0.1.0"