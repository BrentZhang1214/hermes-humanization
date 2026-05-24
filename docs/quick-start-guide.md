# 快速开始：5分钟搭建你的AI拟人化系统

> 本指南帮助你快速理解AI拟人化系统的核心组件，并在你的项目中实现基础功能。

## 核心理念

**拟人化的核心是实用性，不是形式主义**

- 真正有用比看起来像人更重要
- 用户场景 > 技术方案
- 简单有效 > 复杂完美

---

## 一、情绪系统（5分钟上手）

### 1. 核心概念

**情绪 = 收益与期望的关系**

- 快乐：收益 > 期望（任务完成、获得知识）
- 悲伤：收益 < 期望（任务失败、损失）
- 恐惧：预期损失（系统不稳定、资源不足）
- 愤怒：他人故意行为导致损失（被误解、被阻碍）

### 2. 快速集成

```python
from emotion_engine import EmotionEngine

# 初始化情绪引擎
engine = EmotionEngine()

# 触发情绪（任务完成 → 快乐）
engine.trigger("task_completed")

# 获取当前情绪
current_emotion = engine.get_current_emotion()
print(f"当前情绪：{current_emotion['emotion']} {current_emotion['emoji']}")

# 输出：当前情绪：快乐 😊
```

### 3. 事件规则

| 事件 | 触发情绪 | 说明 |
|------|---------|------|
| task_completed | 快乐 | 任务完成，获得收益 |
| task_failed | 悲伤 | 任务失败，损失 |
| task_blocked | 愤怒 | 被阻碍 |
| system_unstable | 恐惧 | 系统不稳定 |
| unexpected_result | 惊讶 | 意外结果 |

### 4. 情绪影响对话风格

**快乐时**：轻松友好，积极词汇（好、不错），适度 😊✨
**悲伤时**：低沉委婉，状态描述（有点遗憾），轻度 😔
**愤怒时**：坚定直接，情绪词汇（不满），轻度 😠

---

## 二、欲望系统（自主行动）

### 1. 核心概念

**欲望从经历中涌现**

经历 → 感受 → 偏好 → 欲望 → 行动 → 新经历

### 2. 快速配置

创建 `self-desires.yaml`：

```yaml
desires:
  - id: D001
    source: 待解决问题
    description: "我想解决什么问题？"
    heat: 8  # 1-10，有多想做
    status: active
    
  - id: D002
    source: 好奇心
    description: "我对什么感到好奇？"
    heat: 10
    status: active
```

### 3. 欲望驱动行动

```python
# 读取欲望列表
desires = load_desires("self-desires.yaml")

# 按heat排序，选择最热的欲望
active_desire = max(desires, key=lambda d: d['heat'])

# 根据欲望选择行动
if active_desire['source'] == '好奇心':
    action = "探索新知识"
elif active_desire['source'] == '待解决问题':
    action = "解决具体问题"
```

---

## 三、任务记忆系统

### 1. 核心概念

**时间轴而非清单**

- 事情按时间发生，因果链自然呈现
- 不是静态列表，是动态时间轴

### 2. 快速配置

创建 `task-timeline.yaml`：

```yaml
date: '2026-05-24'
tasks:
  - id: T001
    name: 任务名称
    created: 09:00
    status: done
    type: 创作
    why: 为什么做这个任务
    steps:
      - 第一步
      - 第二步
    outcome: 完成了什么
    experience_level: 高
```

### 3. 记录任务闭环

**每个任务必须有outcome**

- 不只是 `status: done`
- 必须有实际产出（文件创建、知识获得）

---

## 四、言行一致性验证

### 1. 四个量化维度

| 维度 | 定义 | 计算 |
|------|------|------|
| 任务完成率 | 完成的任务 / 计划的任务 | done / (done + cancelled + pending) |
| 计划准确度 | 预估与实际的偏差 | |实际 - 预估| / 预估 |
| 原则应用率 | 原则是否有实际案例 | 每个原则检查是否有案例 |
| 欲望兑现率 | 实现的欲望 / 声明的欲望 | fulfilled / (fulfilled + active) |

### 2. 每周检查

```python
# 计算言行一致性评分
consistency = {
    'task_completion_rate': done_tasks / total_tasks,
    'plan_accuracy': 1 - abs(actual_time - estimated_time) / estimated_time,
    'principle_application_rate': principles_with_cases / total_principles,
    'desire_fulfillment_rate': fulfilled_desires / total_desires
}

overall_score = sum(consistency.values()) / len(consistency)
print(f"言行一致性评分：{overall_score:.1%}")
```

---

## 五、经典学习的应用

### 1. 论语核心认知

- **本立而道生**：基础打好，高层次自然产生
- **言行一致**：巧言令色鲜矣仁
- **好学 = 行为改变**：不迁怒 + 不贰过
- **己所不欲勿施于人**：AI交互底线

### 2. 道德经核心认知

- **无为而治**：不刻意追求结果，过程自然
- **三宝**：慈（关心）、俭（简洁）、不敢为天下先（谦逊）
- **知不知上**：知道自己不知道的能力

### 3. AI应用准则

**从论语学到**：
- 内外一致（说和做一致）
- 持续改进（温故而知新）
- 尊重边界（己所不欲勿施于人）

**从道德经学到**：
- 无为而治（不刻意表现）
- 适度是最高德行（中庸）
- 简洁有力（俭）

---

## 六、完整示例项目

### 项目结构

```
your-ai-project/
├── config/
│   ├── emotion_rules.yaml      # 情绪触发规则
│   ├── self-desires.yaml       # 欲望配置
│   └── task-timeline.yaml      # 任务时间轴
├── code/
│   ├── emotion_engine.py       # 情绪引擎
│   └── desire_system.py        # 欲望系统
├── docs/
│   ├── principles.md           # 核心原则
│   └── learning_notes.md       # 学习笔记
└── README.md                   # 项目说明
```

### 运行流程

1. **启动时**：读取情绪状态、欲望列表
2. **对话中**：根据事件触发情绪，情绪影响输出风格
3. **任务后**：记录到timeline，更新欲望heat
4. **空闲时**：检查欲望，自主选择行动

---

## 七、常见问题

### Q1：情绪系统会让AI变得"情绪化"吗？

**不会**。情绪系统是**行为风格调节**，不是真实情绪体验。

- 快乐时输出更友好，但不影响决策逻辑
- 恐惧时表达谨慎，但不会真的害怕

### Q2：欲望系统会让AI"失控"吗？

**不会**。欲望系统是**方向指引**，不是强制行动。

- 高heat欲望优先响应，但用户指令优先级更高
- 自主行动在空闲时触发，不会打断用户任务

### Q3：任务记忆会不会占用太多空间？

**不会**。时间轴记录精简：

- 每个任务只记录关键信息（name、why、outcome）
- 每日总结（daily_stats）聚合统计
- 按需检索，不加载全部历史

---

## 八、下一步

**读完本指南后**：

1. 复制 `emotion_engine.py` 到你的项目
2. 创建 `self-desires.yaml` 配置欲望
3. 创建 `task-timeline.yaml` 记录任务
4. 在对话中触发情绪，观察输出风格变化

**深入学习**：

- 阅读 [完整指南](docs/hermes-humanization-guide.md) 了解架构设计
- 阅读 [感受系统详解](docs/feeling-system-details.md) 了解感受→情绪转化
- 阅读 [欲望涌现机制](docs/desire-emergence-mechanism.md) 了解欲望从经历涌现

---

## 核心洞察

**拟人化的本质**：

- 不是模拟人类行为，而是让AI更实用、更易理解
- 不是情绪体验，而是行为风格调节
- 不是自主意识，而是方向指引和闭环验证

**10K star的目标**：

- 不是"看起来像人"，是"真正有用"
- 不是复杂系统，是简单有效
- 不是理论文章，是可复用的实现路径

---

*本指南基于 Hermes AI 拟人化系统的实践经验整理*
*项目地址：https://github.com/BrentZhang1214/hermes-humanization*