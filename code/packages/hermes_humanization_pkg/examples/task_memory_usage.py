"""
完整使用示例：任务记忆系统（v0.2 SQLite版本）
展示如何记录任务、搜索历史、关联概念、构建知识图谱
"""

from hermes_humanization import TaskMemory
from datetime import datetime

# ========== 1. 基础使用（完全兼容v0.1 API） ==========
print("=== 1. 基础使用（兼容v0.1） ===")
# 创建任务记忆系统（自动创建SQLite数据库）
memory = TaskMemory()

# 添加任务并记录详细信息（和v0.1完全一样的API）
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

# 保存（v0.2不需要手动调用_save，自动持久化）
# memory._save()

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

# ========== 2. v0.2 新增功能：事件记录 ==========
print("\n=== 2. v0.2 新增：完整事件记录 ===")
event_id = memory.record_event({
    'type': '创作',
    'description': '完成AI拟人化系统v0.2版本更新',
    'outcome': '成功将记忆系统从文件升级为SQLite知识图谱',
    'why': '支持更复杂的检索和概念关联',
    'value_assessment': 8,
    'experience_level': '高',
    'steps': ["重写task_memory.py", "更新pyproject.toml", "重写示例文件", "更新README"],
    'insights': ["SQLite内置无需额外依赖", "知识图谱让记忆更有价值", "向下兼容减少迁移成本"],
    'files_created': ["examples/concept_graph_usage.py"],
    'files_modified': ["task_memory.py", "pyproject.toml", "README.md", "CHANGELOG.md"]
})
print(f"事件已记录，ID: {event_id}")

# ========== 3. v0.2 新增功能：概念管理 ==========
print("\n=== 3. v0.2 新增：概念管理与关联 ===")
# 添加概念
concept1_id = memory.add_concept({
    'name_zh': 'SQLite',
    'name_en': 'SQLite',
    'kind': 'tool',
    'domain': '数据库',
    'definition': '轻量级嵌入式关系型数据库，内置Python标准库',
    'confidence': '深刻',
    'importance': '核心'
})

concept2_id = memory.add_concept({
    'name_zh': '知识图谱',
    'name_en': 'Knowledge Graph',
    'kind': 'model',
    'domain': '人工智能',
    'definition': '用图结构表示知识和概念之间的关联关系的模型',
    'confidence': '掌握',
    'importance': '重要'
})

concept3_id = memory.add_concept({
    'name_zh': 'AI拟人化',
    'name_en': 'AI Humanization',
    'kind': 'concept',
    'domain': 'AI',
    'definition': '让AI拥有类似人类的情绪、欲望、记忆和行为模式的技术',
    'confidence': '深刻',
    'importance': '核心'
})

print(f"已添加3个概念：{concept1_id}, {concept2_id}, {concept3_id}")

# 关联概念
memory.link_concepts(concept3_id, concept2_id, link_type='part_of', strength=5, note='知识图谱是AI拟人化记忆系统的核心组件')
memory.link_concepts(concept2_id, concept1_id, link_type='built_with', strength=4, note='知识图谱用SQLite实现存储')
print("已关联概念")

# 获取概念图谱
graph = memory.get_concept_graph(concept3_id, max_depth=2)
print(f"\n概念图谱包含 {len(graph['nodes'])} 个节点，{len(graph['edges'])} 条边")
print("节点列表:")
for node in graph['nodes']:
    print(f"  [{node['id']}] {node['name_zh']} ({node['kind']})")

print("\n边列表:")
for edge in graph['edges']:
    print(f"  {edge['from_id']} → {edge['to_id']} ({edge['link_type']}, 强度: {edge['strength']})")
