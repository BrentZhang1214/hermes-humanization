"""
使用示例：情绪引擎基础用法
"""

from hermes_humanization import EmotionEngine

# 创建情绪引擎
engine = EmotionEngine()

print(f"当前情绪: {engine.current_emotion}")
print(f"风格指南: {engine.get_style_guide()}")

# 切换情绪
engine.set_emotion("悲伤")
print(f"\n切换后情绪: {engine.current_emotion}")
print(f"风格指南: {engine.get_style_guide()}")

# 遍历所有情绪
print("\n所有情绪风格:")
for emotion in engine.EMOTIONS:
    engine.set_emotion(emotion)
    style = engine.get_style_guide()
    print(f"  {emotion}: {style['emoji']} {style['tone']}")