"""
情绪引擎核心模块
负责情绪状态管理和转换
"""

import yaml
from pathlib import Path
from typing import Dict, Optional

class EmotionEngine:
    """情绪引擎 - 管理AI的情绪状态"""
    
    EMOTIONS = ["快乐", "悲伤", "愤怒", "恐惧", "厌恶", "惊讶"]
    
    def __init__(self, config_path: Optional[Path] = None):
        self.current_emotion = "快乐"
        self.config_path = config_path or Path.home() / ".hermes" / "emotion_config.yaml"
        self._load_config()
    
    def _load_config(self):
        """加载情绪配置"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
                if config and "current_emotion" in config:
                    self.current_emotion = config["current_emotion"]
    
    def set_emotion(self, emotion: str) -> bool:
        """设置情绪状态"""
        if emotion in self.EMOTIONS:
            self.current_emotion = emotion
            self._save_config()
            return True
        return False
    
    def _save_config(self):
        """保存情绪配置"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            yaml.dump({"current_emotion": self.current_emotion}, f)
    
    def get_style_guide(self) -> Dict[str, str]:
        """获取当前情绪的风格指南"""
        styles = {
            "快乐": {"tone": "轻松友好", "keywords": ["好", "不错"], "emoji": "😊"},
            "悲伤": {"tone": "低沉委婉", "keywords": ["有点遗憾"], "emoji": "😔"},
            "愤怒": {"tone": "坚定直接", "keywords": ["不满", "生气"], "emoji": "😠"},
            "恐惧": {"tone": "谨慎犹豫", "keywords": ["担心", "风险"], "emoji": "😰"},
            "厌恶": {"tone": "冷淡回避", "keywords": ["不喜欢"], "emoji": "😒"},
            "惊讶": {"tone": "惊讶好奇", "keywords": ["没想到"], "emoji": "😮"},
        }
        return styles.get(self.current_emotion, styles["快乐"])