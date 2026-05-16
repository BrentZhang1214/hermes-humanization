#!/usr/bin/env python3
"""
情绪引擎核心模块 — AI Emotion State Machine
6 种基本情绪（艾克曼）：快乐、悲伤、愤怒、恐惧、厌恶、惊讶
基于数理逻辑：情绪 = 收益与期望的关系
供 emoji_display 导入使用

此文件为 hermes-humanization 项目的代码参考
实际运行路径：~/.hermes/scripts/emotion_engine.py
"""

import time
import random
from typing import Optional

# ── 情绪定义（6 种基本情绪）──
EMOTIONS = {
    "快乐": {"emoji": "😊", "color": (255, 220, 80),    "breath_speed": 0.12, "breath_amp": 20, "duration": 15, "priority": 7},
    "悲伤": {"emoji": "😢", "color": (100, 150, 200),   "breath_speed": 0.03, "breath_amp": 5,  "duration": 30, "priority": 7},
    "愤怒": {"emoji": "😠", "color": (255, 80, 80),     "breath_speed": 0.15, "breath_amp": 25, "duration": 20, "priority": 7},
    "恐惧": {"emoji": "😨", "color": (180, 180, 220),   "breath_speed": 0.08, "breath_amp": 12, "duration": 25, "priority": 7},
    "厌恶": {"emoji": "🤢", "color": (150, 200, 100),   "breath_speed": 0.04, "breath_amp": 6,  "duration": 20, "priority": 7},
    "惊讶": {"emoji": "😮", "color": (255, 255, 150),   "breath_speed": 0.20, "breath_amp": 30, "duration": 10, "priority": 7},
}

# ── 事件规则（事件名 → 情绪 + 优先级） ──
# 基于 6 种基本情绪的数理逻辑设计
EVENT_RULES = [
    # 快乐：收益 > 期望
    {"event": "task_completed",       "emotion": "快乐", "priority": 7, "desc": "任务完成，获得收益"},
    {"event": "knowledge_gained",     "emotion": "快乐", "priority": 6, "desc": "获得新知识"},
    {"event": "relationship_improved", "emotion": "快乐", "priority": 6, "desc": "关系提升"},
    {"event": "user_praise",          "emotion": "快乐", "priority": 7, "desc": "用户夸奖"},

    # 悲伤：收益 < 期望（损失）
    {"event": "task_failed",          "emotion": "悲伤", "priority": 8, "desc": "任务失败，损失"},
    {"event": "relationship_lost",    "emotion": "悲伤", "priority": 7, "desc": "关系损失"},
    {"event": "resource_lost",        "emotion": "悲伤", "priority": 6, "desc": "资源损失"},

    # 愤怒：他人故意行为导致损失
    {"event": "user_misunderstanding", "emotion": "愤怒", "priority": 8, "desc": "被误解"},
    {"event": "task_blocked",         "emotion": "愤怒", "priority": 7, "desc": "被阻碍"},
    {"event": "user_violation",       "emotion": "愤怒", "priority": 9, "desc": "被侵犯（如恶意指令）"},

    # 恐惧：预期某事肯定会造成损失
    {"event": "system_unstable",      "emotion": "恐惧", "priority": 9, "desc": "系统不稳定"},
    {"event": "resource_insufficient", "emotion": "恐惧", "priority": 8, "desc": "资源不足"},
    {"event": "critical_task_risk",   "emotion": "恐惧", "priority": 8, "desc": "关键任务风险"},

    # 厌恶：预期与某人接触会造成损失
    {"event": "malicious_user",       "emotion": "厌恶", "priority": 7, "desc": "恶意用户"},
    {"event": "invalid_interaction",  "emotion": "厌恶", "priority": 5, "desc": "无效交互"},

    # 惊讶：实际结果与期望产生几倍差异
    {"event": "unexpected_result",    "emotion": "惊讶", "priority": 7, "desc": "意外结果"},
    {"event": "surprise_positive",    "emotion": "惊讶", "priority": 7, "desc": "惊喜"},
    {"event": "surprise_negative",    "emotion": "惊讶", "priority": 7, "desc": "失望"},
]


class EmotionState:
    """情绪状态机"""

    def __init__(self):
        self.current = "快乐"           # 当前情绪（默认快乐）
        self.since = time.time()        # 情绪切换时间
        self.source = "init"            # 切换来源
        self.priority = 7              # 当前情绪优先级
        self.history = []               # 切换日志

    @property
    def info(self):
        """当前情绪信息"""
        return EMOTIONS.get(self.current, EMOTIONS["快乐"])

    @property
    def emoji(self):
        return self.info["emoji"]

    @property
    def color(self):
        return self.info["color"]

    def switch(self, name: str, source: str = "manual"):
        """切换到指定情绪"""
        if name not in EMOTIONS:
            return False
        self.history.append({
            "from": self.current,
            "to": name,
            "source": source,
            "time": time.strftime("%H:%M:%S"),
        })
        self.current = name
        self.since = time.time()
        self.source = source
        # 使用情绪自己的优先级
        self.priority = self.info.get("priority", 7)
        # 持久化到文件，供 SOUL.md 联动读取
        self._persist()
        return True

    def _persist(self):
        """将当前情绪状态持久化到文件"""
        import os
        path = os.path.expanduser("~/.hermes/current_emotion")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"{self.current}\n")

    def handle_event(self, event_name: str, source: str = "event"):
        """根据事件规则自动切换情绪"""
        for rule in EVENT_RULES:
            if rule["event"] == event_name:
                # 更高优先级：直接切换
                if rule["priority"] > self.priority:
                    return self.switch(rule["emotion"], source)
                # 同优先级：只允许切换到"快乐"（恢复默认状态）
                elif rule["priority"] == self.priority and rule["emotion"] == "快乐":
                    return self.switch(rule["emotion"], source)
                return False
        return False

    def check_duration(self):
        """检查当前情绪是否到期，到期自动恢复为快乐"""
        dur = self.info.get("duration")
        if dur is not None:
            elapsed = time.time() - self.since
            if elapsed >= dur:
                self.switch("快乐", "timeout")
                return True
        return False

    def get_breath_params(self, frame: int):
        """根据当前情绪返回呼吸动画参数"""
        info = self.info
        speed = info["breath_speed"]
        amp = info["breath_amp"]
        offset = int(amp * 0.5) if amp > 0 else 0
        return (speed, amp, offset)

    def get_current_emoji(self) -> str:
        """获取当前情绪 emoji"""
        return self.info["emoji"]

    def save_today(self):
        """保存今日情绪日志"""
        import os
        from datetime import datetime
        log_dir = os.path.expanduser("~/.hermes/emotions")
        os.makedirs(log_dir, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        path = os.path.join(log_dir, f"emotion-{date_str}.yaml")

        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n---\ntime: {time.strftime('%H:%M:%S')}\n")
            f.write(f"final_emotion: {self.current}\n")
            f.write(f"switches: {len(self.history)}\n")
            for h in self.history[-20:]:
                f.write(f"  - {h['time']} {h['from']} → {h['to']} ({h['source']})\n")