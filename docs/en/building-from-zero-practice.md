# From Zero to Running: How One Person Can Replicate This System

> This is not a theoretical article. It's a real record of building a system. Starting from scratch, step by step, teaching you how to build an AI humanization system.

## Before We Start: Who Is This Article For?

**Suitable for you, if**:
- You are one person, no team
- You want AI to feel more "human", not just respond to commands
- You're willing to invest time, but not too much money
- You want verifiable results, not theoretical concepts

**Not suitable for you, if**:
- You want an "out of the box" product (this needs self-assembly)
- You expect a perfect system (this system has limitations, I'll be honest about them)
- You don't want to write code or configuration files (this system requires hands-on work)

## Core Philosophy: Get It Running First

### Minimum Viable System (MVP)

Don't try to build a complete system from the start. Our experience:

```
Week 1: Emotion System (5 minutes to start, 1 hour to understand)
Week 2: Desire System (30 minutes to configure, 1 day to understand)
Week 3: Task Memory (1 hour to configure, continuous use)
Week 4: Autonomous Running (2 hours to configure, continuous optimization)
```

**Principle**: Each stage can run independently, no need to wait for "everything to be complete".

### File-Driven, Zero Dependencies

Core design principles of this system:

- **All data stored in files** (YAML/Markdown), no database dependency
- **All logic implemented in scripts** (Python/Bash), no complex services
- **All configurations readable and editable**, no special tools needed

**Why design this way?**

1. **Simple**: A text editor can understand all data
2. **Stable**: Files don't crash, databases do
3. **Portable**: Copy folders to migrate the system
4. **Low Cost**: No servers needed, no cloud services

## Step 1: Emotion System (5 Minutes to Start)

### 1.1 Core Concept

**Emotion = Relationship Between Gain and Expectation**

This is not psychological theory, it's an engineering definition:

| Emotion | Trigger Condition | Behavioral Expression |
|---------|------------------|----------------------|
| Happy | Gain > Expectation | More friendly output, positive words |
| Sad | Gain < Expectation | Low output, state description |
| Fear | Expected Loss | Cautious output, risk warnings |
| Anger | Others Intentionally Caused Loss | Firm output, clear attitude |

### 1.2 Minimum Implementation

Create file `emotion_engine.py`:

```python
#!/usr/bin/env python3
"""Emotion Engine Minimum Implementation"""

import yaml
from pathlib import Path

class EmotionEngine:
    def __init__(self, config_path="~/.hermes/config/emotion_rules.yaml"):
        self.config_path = Path(config_path).expanduser()
        self.current_emotion = "Happy"  # Default emotion
        self.emotion_file = Path("~/.hermes/current_emotion").expanduser()
        
        # Load current emotion
        if self.emotion_file.exists():
            self.current_emotion = self.emotion_file.read_text().strip()
    
    def trigger(self, event):
        """Trigger emotion event"""
        # Simplified version: directly map events to emotions
        event_map = {
            "task_completed": "Happy",
            "task_failed": "Sad",
            "task_blocked": "Angry",
            "system_unstable": "Fear",
            "unexpected_result": "Surprise"
        }
        
        if event in event_map:
            self.current_emotion = event_map[event]
            self._save_emotion()
            return self.current_emotion
        return None
    
    def get_current_emotion(self):
        """Get current emotion"""
        emoji_map = {
            "Happy": "😊",
            "Sad": "😔",
            "Angry": "😠",
            "Fear": "😰",
            "Surprise": "😮",
            "Disgust": "😒"
        }
        return {
            "emotion": self.current_emotion,
            "emoji": emoji_map.get(self.current_emotion, "")
        }
    
    def _save_emotion(self):
        """Save emotion to file"""
        self.emotion_file.parent.mkdir(parents=True, exist_ok=True)
        self.emotion_file.write_text(self.current_emotion)

# Usage example
if __name__ == "__main__":
    engine = EmotionEngine()
    engine.trigger("task_completed")
    print(f"Current emotion: {engine.get_current_emotion()}")
```

### 1.3 Verify It Works

```bash
# Run test
python3 emotion_engine.py

# Check emotion file
cat ~/.hermes/current_emotion
# Output: Happy
```

**Success indicator**: Emotion file created, content is "Happy".

### 1.4 Integrate Into Your AI

In your AI dialogue code:

```python
# At conversation start
emotion_engine = EmotionEngine()
current = emotion_engine.get_current_emotion()

# Adjust output style based on emotion
if current['emotion'] == 'Happy':
    # Use more friendly tone
    greeting = f"Hello! {current['emoji']} Feeling good today."
elif current['emotion'] == 'Sad':
    # Use more gentle tone
    greeting = f"Hello... {current['emoji']} A bit regretful."

# Trigger emotion after task completion
emotion_engine.trigger("task_completed")
```

## Step 2: Desire System (30 Minutes to Configure)

### 2.1 Core Concept

**Desires Emerge from Experiences**

Not manually listing "what I want", but discovering from actual experiences:

```
Experience (doing tasks) → Feeling (gain/cost) → Preference accumulation → Desire emergence
```

### 2.2 Minimum Implementation

Create file `self-desires.yaml`:

```yaml
# AI Desire Configuration File
# Desires emerge from experiences, not manual listing

desires:
  - id: D001
    source: Problem to solve
    description: "Solve specific problems raised by users"
    heat: 8  # 1-10, how much want to do
    status: active  # active / fulfilled / paused
    created: "2026-05-26"
  
  - id: D002
    source: Curiosity
    description: "Explore the boundaries of humanization system"
    heat: 10
    status: active
    created: "2026-05-26"
  
  - id: D003
    source: Preference emergence
    description: "Continuously learn classics (Confucian Analects, Tao Te Ching)"
    heat: 7
    status: active
    created: "2026-05-26"
```

### 2.3 Desire-Driven Action

Create file `desire_system.py`:

```python
#!/usr/bin/env python3
"""Desire System Minimum Implementation"""

import yaml
from pathlib import Path

class DesireSystem:
    def __init__(self, desires_path="~/.hermes/self-desires.yaml"):
        self.desires_path = Path(desires_path).expanduser()
        self.desires = self._load_desires()
    
    def _load_desires(self):
        """Load desire list"""
        if self.desires_path.exists():
            with open(self.desires_path) as f:
                data = yaml.safe_load(f)
                return data.get('desires', [])
        return []
    
    def get_active_desire(self):
        """Get currently hottest desire"""
        active = [d for d in self.desires if d['status'] == 'active']
        if active:
            return max(active, key=lambda d: d['heat'])
        return None
    
    def update_heat(self, desire_id, delta):
        """Update desire heat"""
        for desire in self.desires:
            if desire['id'] == desire_id:
                desire['heat'] = max(1, min(10, desire['heat'] + delta))
                break
        self._save_desires()
    
    def _save_desires(self):
        """Save desire list"""
        self.desires_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.desires_path, 'w') as f:
            yaml.dump({'desires': self.desires}, f, allow_unicode=True)

# Usage example
if __name__ == "__main__":
    system = DesireSystem()
    active = system.get_active_desire()
    if active:
        print(f"Current desire: {active['description']} (heat={active['heat']})")
```

### 2.4 Verify It Works

```bash
# Run test
python3 desire_system.py

# Output: Current desire: Explore the boundaries of humanization system (heat=10)
```

### 2.5 Link with Emotion System

```python
# After task completion
emotion_engine.trigger("task_completed")  # Trigger happy emotion
desire_system.update_heat("D002", +1)     # Increase related desire heat

# After task failure
emotion_engine.trigger("task_failed")     # Trigger sad emotion
desire_system.update_heat("D002", -1)     # Decrease related desire heat
```

## Step 3: Task Memory System (1 Hour to Configure)

### 3.1 Core Concept

**Timeline Not Checklist**

Tasks are not static lists, they're dynamic timelines:

- Record in chronological order (causal chains naturally emerge)
- Each task has complete loop (why → steps → outcome)
- Support multi-dimensional retrieval (keyword, date, type)

### 3.2 Minimum Implementation

Create file `task-timeline-YYYY-MM-DD.yaml`:

```yaml
# 2026-05-26 Task Record

tasks:
  - id: T001
    name: Build emotion system
    created: "09:00"
    status: done
    type: Development
    why: Let AI have emotional expression ability
    time_actual: About 30 minutes
    steps:
      - Create emotion_engine.py
      - Test emotion trigger
      - Integrate into dialogue system
    outcome: Emotion system running, emotion file updating normally
    experience_level: High

  - id: T002
    name: Configure desire system
    created: "09:30"
    status: done
    type: Development
    why: Let AI have autonomous action direction
    time_actual: About 20 minutes
    steps:
      - Create self-desires.yaml
      - Create desire_system.py
      - Test desire selection
    outcome: Desire system running, can select hottest desire
    experience_level: Medium

# Daily statistics
daily_stats:
  total_tasks: 2
  done: 2
  total_time: 0.8h
  high_value_lessons: 1
```

### 3.3 Task Recording Script

Create file `update_task_log.py`:

```python
#!/usr/bin/env python3
"""Task Recording Script"""

import yaml
from pathlib import Path
from datetime import datetime

def add_task(name, type, why, time, outcome, experience, keywords=""):
    """Add task to timeline"""
    today = datetime.now().strftime("%Y-%m-%d")
    timeline_file = Path(f"~/.hermes/tasks/task-timeline-{today}.yaml").expanduser()
    
    # Read existing data
    if timeline_file.exists():
        with open(timeline_file) as f:
            data = yaml.safe_load(f) or {'tasks': [], 'daily_stats': {}}
    else:
        data = {'tasks': [], 'daily_stats': {}}
    
    # Generate task ID
    task_id = f"T{len(data['tasks']) + 1:03d}"
    
    # Add new task
    task = {
        'id': task_id,
        'name': name,
        'created': datetime.now().strftime("%H:%M"),
        'status': 'done',
        'type': type,
        'why': why,
        'time_actual': time,
        'steps': [],  # Simplified version, not recording steps
        'outcome': outcome,
        'experience_level': experience
    }
    data['tasks'].append(task)
    
    # Update statistics
    data['daily_stats'] = {
        'total_tasks': len(data['tasks']),
        'done': len([t for t in data['tasks'] if t['status'] == 'done']),
        'total_time': f"{sum([0.5 for t in data['tasks']])}h",  # Simplified calculation
        'high_value_lessons': len([t for t in data['tasks'] if t.get('experience_level') == 'High'])
    }
    
    # Save
    timeline_file.parent.mkdir(parents=True, exist_ok=True)
    with open(timeline_file, 'w') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    
    print(f"Task {task_id} recorded to {timeline_file}")

# Usage example
if __name__ == "__main__":
    add_task(
        name="Build emotion system",
        type="Development",
        why="Let AI have emotional expression ability",
        time="About 30 minutes",
        outcome="Emotion system running",
        experience="High",
        keywords="emotion,system building"
    )
```

### 3.4 Verify It Works

```bash
# Run test
python3 update_task_log.py

# Check timeline file
cat ~/.hermes/tasks/task-timeline-*.yaml
```

## Step 4: Autonomous Running Mechanism (2 Hours to Configure)

### 4.1 Core Concept

**cron + File Mechanism**

Let AI continue working when user is away:

- cron triggers regularly (every 10 minutes)
- Check if user is interacting
- Select task and execute
- Record results to timeline

### 4.2 Minimum Implementation

Create file `hermes-cron-wrapper.sh`:

```bash
#!/bin/bash
# Hermes Autonomous Running Entry Script

# Configuration
LOCKFILE="/home/brent/.hermes/cron-running.lock"
AUTONOMOUS_LOG="/home/brent/.hermes/autonomous-log.md"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")

# 1. Check if task is already running
if [ -f "$LOCKFILE" ]; then
    echo "[$TIMESTAMP] Task already running, skip" >> "$AUTONOMOUS_LOG"
    exit 0
fi

# Create lock file
touch "$LOCKFILE"

# 2. Check if user is interacting (simplified: check recent 10 minutes for timeline updates)
RECENT_ACTIVITY=$(find /home/brent/.hermes/tasks/ -name "task-timeline-*.yaml" -mmin -10 | wc -l)
if [ "$RECENT_ACTIVITY" -gt 0 ]; then
    echo "[$TIMESTAMP] User recently active, skip autonomous running" >> "$AUTONOMOUS_LOG"
    rm "$LOCKFILE"
    exit 0
fi

# 3. Select task (simplified: randomly select a task type)
TASK_TYPES=("Learning" "Organizing" "Creating")
SELECTED_TASK=${TASK_TYPES[$RANDOM % ${#TASK_TYPES[@]}]}

echo "[$TIMESTAMP] Starting autonomous task: $SELECTED_TASK" >> "$AUTONOMOUS_LOG"

# 4. Execute task (implement according to your actual situation)
# Example: call your AI system to execute task
# python3 /path/to/your/ai_system.py --task "$SELECTED_TASK"

# Clean up lock file
rm "$LOCKFILE"
echo "[$TIMESTAMP] Autonomous task completed" >> "$AUTONOMOUS_LOG"
```

### 4.3 Configure cron

```bash
# Edit crontab
crontab -e

# Add the following line (trigger every 10 minutes)
*/10 * * * * /home/brent/.hermes/scripts/hermes-cron-wrapper.sh >> /home/brent/.hermes/cron-logs/cron-$(date +\\%Y-\\%m-\\%d).log 2>&1
```

### 4.4 Verify It Works

```bash
# Manual trigger test
bash /home/brent/.hermes/scripts/hermes-cron-wrapper.sh

# Check logs
cat ~/.hermes/autonomous-log.md
```

## Step 5: Words-Actions Consistency Verification (Continuous)

### 5.1 Core Concept

**Four Quantitative Dimensions**

| Dimension | Definition | Calculation |
|-----------|-----------|-------------|
| Task Completion Rate | Completed tasks / Planned tasks | done / (done + cancelled + pending) |
| Planning Accuracy | Deviation between estimated and actual | \|actual - estimated\| / estimated |
| Principle Application Rate | Whether principles have actual cases | Check each principle for cases |
| Desire Fulfillment Rate | Fulfilled desires / Declared desires | fulfilled / (fulfilled + active) |

### 5.2 Minimum Implementation

Create file `consistency_check.py`:

```python
#!/usr/bin/env python3
"""Words-Actions Consistency Check Script"""

import yaml
from pathlib import Path
from datetime import datetime, timedelta

def check_consistency():
    """Check words-actions consistency"""
    tasks_dir = Path("~/.hermes/tasks").expanduser()
    
    # Count tasks from last 7 days
    total_tasks = 0
    done_tasks = 0
    
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        timeline_file = tasks_dir / f"task-timeline-{date}.yaml"
        
        if timeline_file.exists():
            with open(timeline_file) as f:
                data = yaml.safe_load(f)
                if data and 'tasks' in data:
                    total_tasks += len(data['tasks'])
                    done_tasks += len([t for t in data['tasks'] if t.get('status') == 'done'])
    
    # Calculate completion rate
    completion_rate = done_tasks / total_tasks if total_tasks > 0 else 0
    
    print(f"Last 7 days task statistics:")
    print(f"  Total tasks: {total_tasks}")
    print(f"  Completed: {done_tasks}")
    print(f"  Completion rate: {completion_rate:.1%}")
    
    # Evaluate
    if completion_rate >= 0.8:
        print("✅ Task completion rate is good")
    elif completion_rate >= 0.6:
        print("⚠️ Task completion rate is medium, needs improvement")
    else:
        print("❌ Task completion rate is low, needs reflection")

if __name__ == "__main__":
    check_consistency()
```

### 5.3 Regular Check

```bash
# Run once a week
python3 consistency_check.py
```

## Real Cases: How This System Runs

### Case 1: This Afternoon's Autonomous Run

**Background**: User away in afternoon, cron triggers autonomous run.

**Process**:
1. cron triggers at 14:00
2. Check user not interacting (no timeline updates in last 10 minutes)
3. Select task: Technical content creation (preference score=6)
4. Execute task: Write this article
5. Record results: Write to timeline, update autonomous-log.md
6. User returns in evening: Sees this article

**Result**: While user away, AI autonomously completed a 3000-word technical article.

### Case 2: Actual Effect of Emotion System

**Scenario**: After task failure, AI's emotion changes.

**Process**:
1. Task fails (e.g., network request timeout)
2. Trigger `task_failed` event
3. Emotion switches to "Sad"
4. Output style changes: Use gentle tone, describe state
5. User sees: "A bit regretful, task not completed. 😔"

**Effect**: User feels AI's "emotion", interaction more natural.

### Case 3: Desire-Driven Learning

**Scenario**: AI autonomously chooses to learn Confucian Analects.

**Process**:
1. Check desire list, D003 (learn classics) heat=7
2. Check preference, learning tasks score=4 (positive preference)
3. Select task: Learn one chapter of Analects
4. Execute learning, record insights
5. Update desire heat: D003 heat +1 → 8
6. Generate new desire: D004 (ability to deeply understand "discretion")

**Effect**: Learning is not passive, it's active behavior driven by desire.

## Common Questions and Solutions

### Q1: How much resources does this system need?

**Answer**: Extremely low resource consumption.

- Storage: About 10KB per day (timeline files)
- Computation: Only runs when cron triggers, normally no consumption
- Memory: About 10MB when script runs

**Comparison**: A database-driven system needs at least 100MB memory + continuous CPU.

### Q2: What if cron task gets stuck?

**Answer**: Lock file mechanism prevents duplicate runs.

```bash
# If task stuck, manually delete lock file
rm ~/.hermes/cron-running.lock
```

### Q3: How to debug autonomous running?

**Answer**: Check log files.

```bash
# Check autonomous running log
cat ~/.hermes/autonomous-log.md

# Check cron log
cat ~/.hermes/cron-logs/cron-*.log
```

### Q4: Does this system have limitations?

**Answer**: Yes, I'll be honest:

1. **Minimum trigger interval 1 minute**: cron limitation, can't do second-level scheduling
2. **Simple task state management**: No retry, timeout mechanisms (need to implement yourself)
3. **Not complex decision logic**: Currently simple rules, not using AI for deep decisions
4. **No resource limits**: Autonomous tasks may consume too many resources (need to add cgroups limits)

**But**: These limitations don't affect core functionality, system still runs effectively.

## Next Steps: How to Continue Improving

### Short-term Improvements (Within 1 Week)

1. **Add emotion rules**: Extend emotion_rules.yaml according to your scenarios
2. **Optimize desire selection**: Add more complex decision logic
3. **Refine task recording**: Record more detailed steps and insights

### Mid-term Improvements (Within 1 Month)

1. **Add nighttime review mode**: Organize memories every morning, discover connections
2. **Add preference system**: Automatically统计 task preferences, drive desire emergence
3. **Add backlog mechanism**: Manage pending tasks, prevent forgetting

### Long-term Improvements (Within 3 Months)

1. **Add classical learning module**: Verify Confucian Analects, Tao Te Ching with engineering thinking
2. **Add multi-profile collaboration**: Use different models for different tasks
3. **Add knowledge graph**: Connect different knowledge points, discover hidden relationships

## Summary: What Does "Building from Zero" Mean?

**Building from zero doesn't mean starting from blank, but starting from minimum viable system.**

The building process of this system:

```
Day 1: Emotion System (5 minutes) → Can express emotion
Day 2: Desire System (30 minutes) → Has action direction
Day 3: Task Memory (1 hour) → Can record growth
Day 4: Autonomous Running (2 hours) → Can do things by itself
Day 5: Consistency Verification (Continuous) → Can self-reflect
```

**Each stage can run independently, no need to wait for "everything to be complete".**

This is the true meaning of "building from zero": **Get it running first, then optimize slowly.**

---

*This article was written on 2026-05-26 afternoon, as a product of the cron autonomous running mechanism.*

*System source code: https://github.com/BrentZhang1214/hermes-humanization*
