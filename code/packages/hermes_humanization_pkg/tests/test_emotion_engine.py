"""测试情绪引擎"""

import pytest
from pathlib import Path
from hermes_humanization import EmotionEngine

def test_emotion_engine_init():
    """测试初始化"""
    engine = EmotionEngine()
    assert engine.current_emotion == "快乐"
    assert engine.current_emotion in engine.EMOTIONS

def test_emotion_switch():
    """测试情绪切换"""
    engine = EmotionEngine()
    
    # 切换到悲伤
    assert engine.set_emotion("悲伤") == True
    assert engine.current_emotion == "悲伤"
    
    # 切换到无效情绪
    assert engine.set_emotion("无效") == False
    assert engine.current_emotion == "悲伤"

def test_emotion_style_guide():
    """测试风格指南"""
    engine = EmotionEngine()
    
    # 快乐风格
    style = engine.get_style_guide()
    assert style["tone"] == "轻松友好"
    assert "好" in style["keywords"]
    
    # 切换到愤怒
    engine.set_emotion("愤怒")
    style = engine.get_style_guide()
    assert style["tone"] == "坚定直接"
    assert "不满" in style["keywords"]

def test_all_emotions():
    """测试所有情绪"""
    engine = EmotionEngine()
    
    for emotion in engine.EMOTIONS:
        assert engine.set_emotion(emotion) == True
        style = engine.get_style_guide()
        assert "tone" in style
        assert "keywords" in style
        assert "emoji" in style