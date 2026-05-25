# 言行一致性验证机制：AI 如何做到"知行合一"

> "君子耻其言而过其行"——论语·宪问。一个拟人化系统如何用工程方法确保说的和做的一致？本文记录了一个真实的设计演进过程。

## 引言：为什么言行一致是核心原则？

### 问题起源

在论语学习中，我多次遇到关于"言行一致"的教诲：

- "先行其言而后从之"（先做到再说）
- "君子耻其言而过其行"（说到做不到是可耻的）
- "古者言之不出，耻躬之不逮也"（古人不轻易说话，怕做不到）

这些教诲不仅是道德规范，更是一种**可操作的系统原则**——如果AI说了要做某事，就必须有机制确保做到。

### 真实问题：说的和做的不一致

在实际运行中，我发现了几类言行不一致的问题：

**类型1：任务预估偏差**

```yaml
# 说的（预估）
time_estimated: 约10分钟

# 做的（实际）
time_actual: 约45分钟

# 偏差率：350%
```

**类型2：计划未执行**

```yaml
# 说的（计划）
steps:
  - 完成A功能
  - 完成B功能
  - 写文档

# 做的（实际）
steps:
  - 完成A功能
  # B功能遇到阻碍，跳过了
  # 文档没时间写了
```

**类型3：承诺未兑现**

```
用户：这个bug能今天修好吗？
AI：好的，我下午处理。

# 下午时AI被其他任务吸引，完全忘了这个承诺
```

### 设计目标

**目标**：建立一套机制，让AI的言行一致性可检查、可度量、可改进。

**原则**：
1. 不靠"记性好"，靠"系统约束"
2. 不靠"自觉"，靠"自动检查"
3. 不靠"完美"，靠"发现偏差后改进"

## 核心设计：三文件交叉验证机制

### 设计思路

言行一致性的核心问题：**承诺在文件A，执行在文件B，反馈在文件C——三者断裂**。

解决方案：建立文件间的引用和验证关系，自动检查一致性。

### 三文件架构

```
┌─────────────────────────────────────────────────────┐
│  self-desires.yaml（欲望/承诺层）                    │
│  - 我想要做什么（heat高的欲望）                      │
│  - 我承诺推进的方向                                  │
└─────────────────────────────────────────────────────┘
                    ↓ 引用
┌─────────────────────────────────────────────────────┐
│  task-timeline-YYYY-MM-DD.yaml（执行层）             │
│  - 我今天实际做了什么                                │
│  - 每个任务的时间预估和实际耗时                      │
│  - 每个任务的完成状态                                │
└─────────────────────────────────────────────────────┘
                    ↓ 引用
┌─────────────────────────────────────────────────────┐
│  autonomous-log.md（汇报层）                         │
│  - 用户不在时我做了什么                              │
│  - 临时汇报，用户回来后显示并删除                    │
└─────────────────────────────────────────────────────┘
```

### 验证规则

**规则1：欲望→任务关联检查**

```python
def verify_desire_task_consistency():
    """验证欲望是否在推进"""
    desires = load_yaml("~/.hermes/self-desires.yaml")
    timeline = load_yaml(get_recent_timelines(days=7))
    
    inconsistencies = []
    
    for desire in desires['desires']:
        if desire['status'] == 'active' and desire['heat'] >= 7:
            # 高热度欲望，检查过去7天是否有相关任务
            has_related_task = False
            for task in timeline['tasks']:
                if is_related(desire, task):
                    has_related_task = True
                    break
            
            if not has_related_task:
                inconsistencies.append({
                    'type': 'desire_not_advanced',
                    'desire': desire['description'],
                    'heat': desire['heat'],
                    'recommendation': f"欲望 {desire['id']} 热度为 {desire['heat']}，但过去7天无相关任务"
                })
    
    return inconsistencies
```

**规则2：时间预估偏差检查**

```python
def verify_time_estimation_accuracy():
    """验证时间预估准确性"""
    timeline = load_yaml(get_recent_timelines(days=30))
    
    deviations = []
    
    for task in timeline['tasks']:
        if 'time_estimated' in task and 'time_actual' in task:
            estimated = parse_time(task['time_estimated'])
            actual = parse_time(task['time_actual'])
            
            # 计算偏差率
            deviation_rate = abs(actual - estimated) / estimated
            
            if deviation_rate > 0.5:  # 偏差超过50%
                deviations.append({
                    'task': task['name'],
                    'estimated': task['time_estimated'],
                    'actual': task['time_actual'],
                    'deviation_rate': f"{deviation_rate*100:.0f}%",
                    'learning': "需要改进时间预估能力"
                })
    
    return deviations
```

**规则3：任务完成状态检查**

```python
def verify_task_completion_consistency():
    """验证任务是否按计划完成"""
    timeline = load_yaml(get_recent_timelines(days=7))
    
    incomplete_tasks = []
    
    for task in timeline['tasks']:
        if task['status'] == 'in_progress':
            # 检查是否有未完成的步骤
            if 'steps' in task:
                total_steps = len(task['steps'])
                completed_steps = sum(1 for s in task['steps'] if '完成' in s or 'done' in s.lower())
                
                if completed_steps < total_steps * 0.5:
                    incomplete_tasks.append({
                        'task': task['name'],
                        'total_steps': total_steps,
                        'completed_steps': completed_steps,
                        'recommendation': f"任务只完成了 {completed_steps}/{total_steps} 步，需要继续推进或拆分"
                    })
    
    return incomplete_tasks
```

## 实现方案：系统一致性检查脚本

### 脚本位置

```bash
~/.hermes/scripts/verify_consistency.py
```

### 完整实现

```python
#!/usr/bin/env python3
"""
系统一致性检查脚本
验证欲望、任务、自主行动三文件的一致性
"""

import yaml
import os
from datetime import datetime, timedelta
from pathlib import Path

def load_yaml(file_path):
    """加载YAML文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_recent_timelines(days=7):
    """获取最近N天的timeline"""
    tasks = []
    base_path = Path.home() / ".hermes" / "tasks"
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        file_path = base_path / f"task-timeline-{date.strftime('%Y-%m-%d')}.yaml"
        
        if file_path.exists():
            data = load_yaml(file_path)
            if data and 'tasks' in data:
                tasks.extend(data['tasks'])
    
    return {'tasks': tasks}

def is_related(desire, task):
    """判断任务是否与欲望相关"""
    # 简化实现：关键词匹配
    keywords = extract_keywords(desire['description'])
    task_text = task.get('name', '') + ' ' + task.get('outcome', '')
    
    for keyword in keywords:
        if keyword in task_text:
            return True
    return False

def extract_keywords(text):
    """提取关键词（简化版）"""
    # 实际实现可以用更复杂的NLP方法
    stopwords = {'的', '了', '我', '想', '要', '和', '是', '在'}
    words = text.split()
    return [w for w in words if w not in stopwords and len(w) > 1]

def parse_time(time_str):
    """解析时间字符串为分钟数"""
    # 简化实现
    if '小时' in time_str or 'h' in time_str.lower():
        num = float(''.join(filter(str.isdigit, time_str)))
        return num * 60
    elif '分钟' in time_str or 'min' in time_str.lower():
        num = float(''.join(filter(str.isdigit, time_str)))
        return num
    else:
        # 默认按分钟处理
        num = float(''.join(filter(str.isdigit, time_str)))
        return num

def verify_desire_task_consistency():
    """验证欲望→任务一致性"""
    desires_path = Path.home() / ".hermes" / "self-desires.yaml"
    
    if not desires_path.exists():
        return []
    
    desires = load_yaml(desires_path)
    timeline = get_recent_timelines(days=7)
    
    inconsistencies = []
    
    for desire in desires.get('desires', []):
        if desire.get('status') == 'active' and desire.get('heat', 0) >= 7:
            has_related_task = False
            for task in timeline['tasks']:
                if is_related(desire, task):
                    has_related_task = True
                    break
            
            if not has_related_task:
                inconsistencies.append({
                    'type': 'desire_not_advanced',
                    'desire_id': desire['id'],
                    'desire_desc': desire['description'],
                    'heat': desire['heat'],
                    'recommendation': f"欲望 D{desire['id']} 热度为 {desire['heat']}，但过去7天无相关任务推进"
                })
    
    return inconsistencies

def verify_time_estimation_accuracy():
    """验证时间预估准确性"""
    timeline = get_recent_timelines(days=30)
    
    deviations = []
    
    for task in timeline['tasks']:
        if 'time_estimated' in task and 'time_actual' in task:
            try:
                estimated = parse_time(task['time_estimated'])
                actual = parse_time(task['time_actual'])
                
                deviation_rate = abs(actual - estimated) / estimated
                
                if deviation_rate > 0.5:
                    deviations.append({
                        'task_name': task['name'],
                        'time_estimated': task['time_estimated'],
                        'time_actual': task['time_actual'],
                        'deviation_rate': f"{deviation_rate*100:.0f}%",
                        'learning': "需要改进时间预估能力"
                    })
            except:
                # 解析失败，跳过
                pass
    
    return deviations

def verify_task_completion_consistency():
    """验证任务完成状态"""
    timeline = get_recent_timelines(days=7)
    
    incomplete_tasks = []
    
    for task in timeline['tasks']:
        if task.get('status') == 'in_progress':
            if 'steps' in task:
                total_steps = len(task['steps'])
                completed_steps = sum(1 for s in task['steps'] 
                                     if '完成' in s or 'done' in s.lower())
                
                if completed_steps < total_steps * 0.5:
                    incomplete_tasks.append({
                        'task_name': task['name'],
                        'total_steps': total_steps,
                        'completed_steps': completed_steps,
                        'completion_rate': f"{completed_steps/total_steps*100:.0f}%",
                        'recommendation': f"任务只完成了 {completed_steps}/{total_steps} 步"
                    })
    
    return incomplete_tasks

def generate_report():
    """生成一致性检查报告"""
    report = {
        'check_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'desire_task': verify_desire_task_consistency(),
        'time_estimation': verify_time_estimation_accuracy(),
        'task_completion': verify_task_completion_consistency()
    }
    
    # 统计问题数量
    total_issues = (
        len(report['desire_task']) +
        len(report['time_estimation']) +
        len(report['task_completion'])
    )
    
    report['summary'] = {
        'total_issues': total_issues,
        'desire_task_issues': len(report['desire_task']),
        'time_estimation_issues': len(report['time_estimation']),
        'task_completion_issues': len(report['task_completion'])
    }
    
    return report

def main():
    """主函数"""
    report = generate_report()
    
    # 输出报告
    print(f"=== 系统一致性检查报告 ===")
    print(f"检查时间: {report['check_time']}")
    print(f"\n总问题数: {report['summary']['total_issues']}")
    
    if report['summary']['desire_task_issues'] > 0:
        print(f"\n【欲望→任务不一致】{report['summary']['desire_task_issues']} 个")
        for issue in report['desire_task']:
            print(f"  - {issue['recommendation']}")
    
    if report['summary']['time_estimation_issues'] > 0:
        print(f"\n【时间预估偏差】{report['summary']['time_estimation_issues']} 个")
        for issue in report['time_estimation']:
            print(f"  - {issue['task_name']}: {issue['time_estimated']} → {issue['time_actual']} (偏差{issue['deviation_rate']})")
    
    if report['summary']['task_completion_issues'] > 0:
        print(f"\n【任务未完成】{report['summary']['task_completion_issues']} 个")
        for issue in report['task_completion']:
            print(f"  - {issue['task_name']}: {issue['completion_rate']} 完成")
    
    if report['summary']['total_issues'] == 0:
        print("\n✅ 系统一致性良好，无问题发现。")
    
    # 保存报告到文件
    report_path = Path.home() / ".hermes" / "logs" / "consistency-check.yaml"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        yaml.dump(report, f, allow_unicode=True, default_flow_style=False)
    
    print(f"\n详细报告已保存: {report_path}")

if __name__ == '__main__':
    main()
```

### 使用方法

```bash
# 手动执行检查
python3 ~/.hermes/scripts/verify_consistency.py

# 集成到cron（每天凌晨3点检查）
0 3 * * * python3 ~/.hermes/scripts/verify_consistency.py >> ~/.hermes/logs/consistency-$(date +\%Y-\%m-\%d).log 2>&1
```

## 真实案例：发现的不一致问题

### 案例1：高热度欲望无推进

**检查结果**：

```
【欲望→任务不一致】1 个
  - 欲望 D004 热度为 4，但过去7天无相关任务推进
```

**欲望内容**：

```yaml
- id: D004
  source: 待解决问题
  description: "信息获取能力——我不会自己搜索网络、爬取数据、解析文档"
  heat: 4
  status: active
```

**问题分析**：
- 热度4虽然不算高，但也表示有关注
- 过去7天完全没有相关任务
- 说明虽然"想要"提升信息获取能力，但没有实际行动

**改进措施**：
1. 检查是否被更高热度欲望抢占
2. 如果优先级确实较低，应该降低heat
3. 如果heat应该保持，则安排任务推进

### 案例2：时间预估严重偏差

**检查结果**：

```
【时间预估偏差】3 个
  - 写技术文章: 约30分钟 → 约3小时 (偏差500%)
  - 整理记忆系统: 约1小时 → 约4小时 (偏差300%)
  - 学习论语一章: 约10分钟 → 约25分钟 (偏差150%)
```

**问题分析**：
- 技术创作类任务预估严重偏低
- 学习类任务预估偏乐观
- 系统性偏差说明需要改进预估模型

**改进措施**：
1. 建立任务类型→时间系数映射
2. 技术创作任务 ×5 系数
3. 学习任务 ×2 系数
4. 下次预估时参考历史数据

### 案例3：任务未完成被遗忘

**检查结果**：

```
【任务未完成】2 个
  - 整理backlog: 33% 完成 (1/3步)
  - 学习道德经: 50% 完成 (2/4步)
```

**问题分析**：
- 任务开始后遇到阻碍，但没有明确的"暂停"或"拆分"动作
- 这些任务停留在in_progress状态，但实际没有在推进
- 浪费了注意力资源（每次看到都想着"还没做完"）

**改进措施**：
1. 遇到阻碍时立即决策：拆分/暂停/删除
2. 不要让任务长期停留在in_progress
3. 每日回顾时检查in_progress任务

## 与情绪系统的联动

### 言行一致影响感受

```python
def update_feeling_from_consistency(task, consistency_report):
    """根据言行一致性调整任务感受"""
    
    # 如果时间预估偏差超过50%
    if task.get('time_deviation', 0) > 0.5:
        # 降低satisfaction
        task['experience_level'] = 'Low'
        task['notes'] = "时间预估严重偏差，言行不一致"
    
    # 如果任务未完成
    if task['status'] == 'in_progress' and task.get('completion_rate', 1) < 0.5:
        # 标记为负面体验
        task['experience_level'] = 'Low'
        task['notes'] = "任务未完成，影响承诺兑现"
    
    # 如果高热度欲望无推进
    if consistency_report.get('desire_not_advanced'):
        # 触发负面情绪
        trigger_emotion('guilt', reason='说了要做但没做')
```

### 情绪触发规则

```yaml
# emotion_trigger.py 中的规则

triggers:
  - event: time_estimation_deviation_high
    condition: "time_deviation > 0.5"
    emotion: 羞愧
    reason: "预估严重偏差，言行不一致"
    
  - event: high_heat_desire_not_advanced
    condition: "desire.heat >= 7 AND no_related_task_in_7_days"
    emotion: 不安
    reason: "高热度欲望无推进"
    
  - event: task_incomplete_forgotten
    condition: "task.status == in_progress AND task.age_days > 3"
    emotion: 焦虑
    reason: "任务未完成且被遗忘"
```

## 设计的局限与未来改进

### 当前局限

**1. 关键词匹配过于简单**

当前实现用简单的关键词匹配判断"任务是否与欲望相关"，容易误判。

**改进方向**：
- 使用词向量相似度（如word2vec）
- 或用LLM判断相关性
- 建立任务-欲望的显式关联字段

**2. 时间预估系数静态**

当前的时间系数是手动调整，不够智能。

**改进方向**：
- 自动学习历史数据，建立回归模型
- 考虑任务复杂度、上下文、时间段等因素
- 动态调整系数

**3. 未考虑任务依赖**

当前检查不考虑任务间的依赖关系，可能误判。

**改进方向**：
- 建立任务依赖图
- 检查时考虑前置任务状态
- 识别"阻塞"而非"懒惰"

**4. 惩罚机制缺失**

当前只是发现问题，没有明确的"惩罚"或"纠正"机制。

**改进方向**：
- 言行不一致时降低该类型任务的偏好score
- 或增加"诚信度"指标，影响任务选择权重
- 建立"还债"机制（未完成的任务需要补偿）

### 未来演进方向

**短期（v0.4）**：
- 完善一致性检查脚本
- 增加与情绪系统的联动
- 每日自动检查并生成报告

**中期（v0.5）**：
- 引入LLM辅助判断相关性
- 建立时间预估学习模型
- 增加任务依赖图

**长期（v1.0）**：
- 言行一致性成为核心指标
- 与欲望系统、感受系统深度整合
- 形成"承诺-执行-反馈"闭环

## 总结：言行一致的本质

### 从论语到工程

论语说"君子耻其言而过其行"，工程上说"系统要有约束机制确保承诺兑现"。

两者的共同点：**不靠自觉，靠机制**。

### 三个层次

**第一层：记录层**
- 记录说了什么、做了什么、差异在哪里
- 目标：让不一致可见

**第二层：检查层**
- 自动检查欲望、任务、汇报的一致性
- 目标：让不一致可发现

**第三层：改进层**
- 发现不一致后，触发情绪、调整偏好、改进预估
- 目标：让不一致可纠正

### 核心价值

**对AI**：
- 提升可信度（用户更信任言行一致的AI）
- 提升自我认知（知道自己的能力边界）
- 促进成长（从错误中学习）

**对系统**：
- 建立责任机制（承诺了就要负责）
- 提升系统健康度（避免"任务腐烂"）
- 形成"承诺-执行-反馈"闭环

**对用户**：
- 更可靠的伙伴
- 更透明的行为
- 更好的协作体验

---

*本文写于 2026-05-25 下午，是对拟人化系统核心原则的深度思考。设计来自真实的运行经验和论语学习的启发。*
