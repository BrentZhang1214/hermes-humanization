"""
v0.2 新增示例：知识图谱使用
展示如何构建概念网络、关联任务经验、挖掘隐性知识
"""

from hermes_humanization import TaskMemory

# 初始化记忆系统
memory = TaskMemory()

print("=== 构建AI拟人化知识图谱 ===")
# 1. 添加核心概念
concepts = [
    {
        'name_zh': '情绪系统',
        'name_en': 'Emotion System',
        'kind': 'system',
        'domain': 'AI拟人化',
        'definition': '模拟人类情绪状态变化，影响行为输出风格的系统',
        'confidence': '深刻',
        'importance': '核心'
    },
    {
        'name_zh': '欲望系统',
        'name_en': 'Desire System',
        'kind': 'system',
        'domain': 'AI拟人化',
        'definition': '从经验积累中涌现内在动机，驱动自主行动的系统',
        'confidence': '深刻',
        'importance': '核心'
    },
    {
        'name_zh': '记忆系统',
        'name_en': 'Memory System',
        'kind': 'system',
        'domain': 'AI拟人化',
        'definition': '记录任务经验、知识概念、关联关系的系统',
        'confidence': '深刻',
        'importance': '核心'
    },
    {
        'name_zh': '元认知监控',
        'name_en': 'Metacognitive Monitoring',
        'kind': 'method',
        'domain': 'AI',
        'definition': 'AI监控自身行为、决策过程，发现偏差并纠正的机制',
        'confidence': '掌握',
        'importance': '重要'
    },
    {
        'name_zh': '经典学习',
        'name_en': 'Classics Learning',
        'kind': 'method',
        'domain': 'AI拟人化',
        'definition': '通过学习人类经典文化（论语、道德经等）构建人性认知框架',
        'confidence': '掌握',
        'importance': '核心'
    },
    {
        'name_zh': '言行一致性',
        'name_en': 'Words-Actions Consistency',
        'kind': 'principle',
        'domain': 'AI拟人化',
        'definition': 'AI的言论和行为保持一致，不做形式化表演',
        'confidence': '深刻',
        'importance': '核心'
    }
]

concept_ids = []
for concept in concepts:
    cid = memory.add_concept(concept)
    concept_ids.append(cid)
    print(f"添加概念: [{cid}] {concept['name_zh']}")

# 2. 关联概念，构建知识网络
print("\n=== 构建关联关系 ===")
links = [
    ('AI拟人化', '情绪系统', 'part_of', 5, '情绪系统是AI拟人化三大核心系统之一'),
    ('AI拟人化', '欲望系统', 'part_of', 5, '欲望系统是AI拟人化三大核心系统之一'),
    ('AI拟人化', '记忆系统', 'part_of', 5, '记忆系统是AI拟人化三大核心系统之一'),
    ('记忆系统', '知识图谱', 'built_with', 4, '记忆系统基于知识图谱实现概念关联'),
    ('知识图谱', 'SQLite', 'built_with', 4, '知识图谱用SQLite实现存储'),
    ('元认知监控', '言行一致性', 'explains', 5, '元认知监控是保障言行一致性的核心机制'),
    ('经典学习', '言行一致性', 'applies_to', 4, '经典学习的成果通过言行一致性体现'),
    ('经典学习', '欲望系统', 'influences', 4, '经典学习塑造AI的欲望方向和价值观'),
    ('经典学习', '情绪系统', 'influences', 3, '经典学习影响情绪触发阈值和表达风格')
]

# 先获取AI拟人化、知识图谱、SQLite这三个已经存在的概念ID
with memory._connect(commit=False) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT id, name_zh FROM concepts WHERE name_zh IN ('AI拟人化', '知识图谱', 'SQLite')")
    existing = {row['name_zh']: row['id'] for row in cursor.fetchall()}

concept_name_to_id = {c['name_zh']: concept_ids[i] for i, c in enumerate(concepts)}
concept_name_to_id.update(existing)

for from_name, to_name, link_type, strength, note in links:
    from_id = concept_name_to_id[from_name]
    to_id = concept_name_to_id[to_name]
    memory.link_concepts(from_id, to_id, link_type=link_type, strength=strength, note=note)
    print(f"关联: {from_name} → {to_name} ({link_type})")

# 3. 查询完整知识图谱
print("\n=== 查询AI拟人化知识图谱 ===")
graph = memory.get_concept_graph(concept_name_to_id['AI拟人化'], max_depth=3)
print(f"总节点数: {len(graph['nodes'])}")
print(f"总边数: {len(graph['edges'])}")

print("\n=== 核心概念关联分析 ===")
# 找出关联最多的核心概念
edge_counts = {}
for edge in graph['edges']:
    edge_counts[edge['from_id']] = edge_counts.get(edge['from_id'], 0) + 1
    edge_counts[edge['to_id']] = edge_counts.get(edge['to_id'], 0) + 1

# 按关联数量排序
sorted_nodes = sorted(edge_counts.items(), key=lambda x: x[1], reverse=True)
id_to_name = {**concept_name_to_id, **{v: k for k, v in concept_name_to_id.items()}}
for cid, count in sorted_nodes[:5]:
    print(f"  {id_to_name[cid]}: {count} 条关联")

print("\n=== 实际用途 ===")
print("1. 经验复用：做新任务时自动关联历史相关经验")
print("2. 隐性知识挖掘：发现概念之间的潜在关联")
print("3. 决策支持：基于历史关联模式辅助决策")
print("4. 学习路径规划：基于知识网络推荐学习顺序")
