"""
使用示例：欲望系统基础用法
"""

from hermes_humanization import DesireSystem

# 创建欲望系统
system = DesireSystem()

# 添加欲望
d1 = system.add_desire("学习道德经", heat=8.0)
d2 = system.add_desire("完善Python包", heat=6.0)
d3 = system.add_desire("探索新工具", heat=4.0)

print("当前欲望列表:")
for desire in system.desires:
    print(f"  [{desire.id}] {desire.content} - 热度: {desire.heat}")

# 模拟时间流逝（欲望衰减）
print("\n模拟时间流逝...")
for desire in system.desires:
    desire.decay(rate=1.0)
    print(f"  [{desire.id}] 热度降至: {desire.heat}")

# 获取活跃欲望
active = system.get_active_desires()
print(f"\n活跃欲望数量: {len(active)}")