"""
完整使用示例：任务记忆系统
展示如何记录任务、搜索历史、分析经验
"""

from hermes_humanization import TaskMemory
from datetime import datetime

# 创建任务记忆系统
memory = TaskMemory()

# 添加任务并记录详细信息
task1 = memory.add_task(
    name="完成Python包开发",
    task_type="技术实现",
    why="推进B091（可复用代码模块）"
)

# 更新任务状态（模拟任务执行）
task1.status = "in_progress"
task1.steps = [
    "创建包结构",
    "编写核心模块",
    "添加测试文件",
    "创建使用示例"
]

# 添加任务结果
task1.outcome = "成功创建hermes-humanization包，包含4个核心模块"
task1.insights = [
    "包结构应该清晰，src/目录放源代码",
    "测试文件确保质量",
    "示例文件帮助用户快速上手"
]
task1.files_created = [
    "emotion_engine.py",
    "desire_system.py",
    "task_memory.py",
    "verification.py"
]

# 保存
memory._save()

# 搜索历史任务
print("搜索关键词'Python':")
results = memory.search_by_keyword("Python")
for task in results:
    print(f"  [{task.id}] {task.name} - {task.status}")

# 获取最近任务
print("\n最近任务:")
recent = memory.get_recent_tasks(limit=5)
for task in recent:
    print(f"  [{task.id}] {task.name} ({task.task_type})")