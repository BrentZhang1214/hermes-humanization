"""测试欲望系统"""

import pytest
from hermes_humanization import DesireSystem, Desire

def test_desire_system_init():
    """测试初始化"""
    system = DesireSystem()
    assert isinstance(system.desires, list)

def test_add_desire():
    """测试添加欲望"""
    system = DesireSystem()
    
    desire = system.add_desire("我想学习新技能", heat=5.0)
    assert desire.id.startswith("D")
    assert desire.content == "我想学习新技能"
    assert desire.heat == 5.0
    assert desire.status == "active"

def test_desire_decay():
    """测试欲望衰减"""
    desire = Desire(id="D001", content="测试", heat=10.0)
    
    desire.decay(rate=3.0)
    assert desire.heat == 7.0
    
    desire.decay(rate=10.0)
    assert desire.heat == 0.0  # 不会变成负数

def test_get_active_desires():
    """测试获取活跃欲望"""
    system = DesireSystem()
    
    system.add_desire("活跃欲望1", heat=5.0)
    system.add_desire("冷却欲望", heat=0.0)
    
    active = system.get_active_desires()
    assert len(active) == 1
    assert active[0].content == "活跃欲望1"