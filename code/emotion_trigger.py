#!/usr/bin/env python3
"""
情绪触发脚本 — 不依赖 emoji_display API 的情绪切换方式
用法：
  python3 emotion_trigger.py 快乐         # 切换到指定情绪
  python3 emotion_trigger.py event task_completed  # 触发事件
  python3 emotion_trigger.py status       # 查看当前情绪

此文件为 hermes-humanization 项目的代码参考
实际运行路径：~/.hermes/scripts/emotion_trigger.py
"""

import sys
import os

sys.path.insert(0, os.path.expanduser("~/.hermes/scripts"))
import emotion_engine

# 情绪状态文件路径（和 engine 内部一致）
STATE_FILE = os.path.expanduser("~/.hermes/current_emotion")


def read_current():
    """读取持久化的当前情绪"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "快乐"  # 默认


def main():
    if len(sys.argv) < 2:
        print(f"当前情绪: {read_current()}")
        print("\n用法:")
        print("  emotion_trigger.py <情绪名>       — 切换情绪")
        print("  emotion_trigger.py event <事件名>  — 触发事件")
        print("  emotion_trigger.py status          — 查看当前情绪")
        print(f"\n可用情绪: {', '.join(emotion_engine.EMOTIONS.keys())}")
        print(f"可用事件: {', '.join(r['event'] for r in emotion_engine.EVENT_RULES)}")
        return

    cmd = sys.argv[1]

    # 创建临时状态机，从持久化文件恢复当前状态
    state = emotion_engine.EmotionState()
    current = read_current()
    if current in emotion_engine.EMOTIONS:
        state.current = current
        state.source = "restored"

    if cmd == "status":
        print(f"当前情绪: {state.current}")

    elif cmd == "event":
        if len(sys.argv) < 3:
            print("需要指定事件名")
            print(f"可用事件: {', '.join(r['event'] for r in emotion_engine.EVENT_RULES)}")
            return
        event_name = sys.argv[2]
        result = state.handle_event(event_name, "trigger-script")
        if result:
            print(f"事件 '{event_name}' → 情绪切换到 '{state.current}'")
        else:
            print(f"事件 '{event_name}' — 当前情绪 '{state.current}'(优先级{state.priority})未被覆盖")

    elif cmd in emotion_engine.EMOTIONS:
        state.switch(cmd, "trigger-script")
        print(f"情绪切换到 '{cmd}'")

    else:
        print(f"未知情绪: {cmd}")
        print(f"可用情绪: {', '.join(emotion_engine.EMOTIONS.keys())}")


if __name__ == "__main__":
    main()