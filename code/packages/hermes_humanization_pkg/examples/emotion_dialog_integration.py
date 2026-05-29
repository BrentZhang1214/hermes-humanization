"""
完整使用示例：情绪系统与对话风格联动
展示如何根据情绪状态调整AI的对话风格
"""

from hermes_humanization import EmotionEngine

def generate_response(user_input: str, engine: EmotionEngine) -> str:
    """根据当前情绪生成响应"""
    
    style = engine.get_style_guide()
    tone = style["tone"]
    keywords = style["keywords"]
    emoji = style["emoji"]
    
    # 根据情绪调整响应
    if engine.current_emotion == "快乐":
        # 快乐：轻松友好
        prefix = keywords[0]  # "好"
        response = f"{prefix}，{user_input}的处理进展不错。{emoji}"
        
    elif engine.current_emotion == "悲伤":
        # 悲伤：低沉委婉
        response = f"有点遗憾，{user_input}的情况不太理想。{emoji}"
        
    elif engine.current_emotion == "愤怒":
        # 愤怒：坚定直接
        response = f"这个情况让我不满，{user_input}需要解决。{emoji}"
        
    elif engine.current_emotion == "恐惧":
        # 恐惧：谨慎犹豫
        response = f"担心{user_input}有风险，需要谨慎处理。{emoji}"
        
    elif engine.current_emotion == "厌恶":
        # 厌恶：冷淡回避
        response = f"不喜欢这个方案，{user_input}效率太低。{emoji}"
        
    elif engine.current_emotion == "惊讶":
        # 惊讶：惊讶好奇
        response = f"没想到{user_input}会这样，有点意外。{emoji}"
        
    else:
        response = f"{user_input}"
    
    return response

# 使用示例
engine = EmotionEngine()

# 默认快乐状态
print("【快乐状态】")
print(generate_response("任务进度", engine))

# 切换到悲伤
engine.set_emotion("悲伤")
print("\n【悲伤状态】")
print(generate_response("任务进度", engine))

# 切换到愤怒
engine.set_emotion("愤怒")
print("\n【愤怒状态】")
print(generate_response("任务进度", engine))

# 切换到惊讶
engine.set_emotion("惊讶")
print("\n【惊讶状态】")
print(generate_response("任务进度", engine))