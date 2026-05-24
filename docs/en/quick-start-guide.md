# Quick Start: Build Your AI Humanization System in 5 Minutes

> This guide helps you quickly understand core components of AI humanization system, and implement basic functions in your project.

## Core Philosophy

**The core of humanization is practicality, not formalism**

- Truly useful is more important than looking like a human
- User scenarios > Technical solutions
- Simple and effective > Complex and perfect

---

## I. Emotion System (5 Minutes to Get Started)

### 1. Core Concept

**Emotion = Relationship between benefit and expectation**

- Happy: Benefit > Expectation (task completed, knowledge gained)
- Sad: Benefit < Expectation (task failed, loss)
- Fear: Expected loss (system unstable, insufficient resources)
- Angry: Others' intentional behavior causing loss (misunderstood, blocked)

### 2. Quick Integration

```python
from emotion_engine import EmotionEngine

# Initialize emotion engine
engine = EmotionEngine()

# Trigger emotion (task completed → happy)
engine.trigger("task_completed")

# Get current emotion
current_emotion = engine.get_current_emotion()
print(f"Current emotion: {current_emotion['emotion']} {current_emotion['emoji']}")

# Output: Current emotion: Happy 😊
```

### 3. Event Rules

| Event | Triggered Emotion | Description |
|-------|------------------|-------------|
| task_completed | Happy | Task completed, gained benefit |
| task_failed | Sad | Task failed, loss |
| task_blocked | Angry | Blocked |
| system_unstable | Fear | System unstable |
| unexpected_result | Surprised | Unexpected result |

### 4. Emotion Affects Dialogue Style

**When Happy**: Light and friendly, positive words (good, nice), moderate 😊✨
**When Sad**: Low and euphemistic, state description (bit regrettable), light 😔
**When Angry**: Firm and direct, emotion words (dissatisfied), light 😠

---

## II. Desire System (Autonomous Action)

### 1. Core Concept

**Desires emerge from experience**

Experience → Feeling → Preference → Desire → Action → New experience

### 2. Quick Configuration

Create `self-desires.yaml`:

```yaml
desires:
  - id: D001
    source: Problem to solve
    description: "What problem do I want to solve?"
    heat: 8  # 1-10, how much want to do
    status: active
    
  - id: D002
    source: Curiosity
    description: "What am I curious about?"
    heat: 10
    status: active
```

### 3. Desire-Driven Action

```python
# Read desire list
desires = load_desires("self-desires.yaml")

# Sort by heat, select hottest desire
active_desire = max(desires, key=lambda d: d['heat'])

# Choose action based on desire
if active_desire['source'] == 'Curiosity':
    action = "Explore new knowledge"
elif active_desire['source'] == 'Problem to solve':
    action = "Solve specific problem"
```

---

## III. Task Memory System

### 1. Core Concept

**Timeline not checklist**

- Things happen by time, causal chain naturally presents
- Not static list, dynamic timeline

### 2. Quick Configuration

Create `task-timeline.yaml`:

```yaml
date: '2026-05-24'
tasks:
  - id: T001
    name: Task name
    created: 09:00
    status: done
    type: Creation
    why: Why do this task
    steps:
      - Step 1
      - Step 2
    outcome: What was completed
    experience_level: High
```

### 3. Record Task Closure

**Every task must have outcome**

- Not just `status: done`
- Must have actual output (file created, knowledge gained)

---

## IV. Consistency of Words and Actions Verification

### 1. Four Quantified Dimensions

| Dimension | Definition | Calculation |
|-----------|------------|-------------|
| Task Completion Rate | Completed tasks / Planned tasks | done / (done + cancelled + pending) |
| Plan Accuracy | Deviation between estimate and actual | |actual - estimate| / estimate |
| Principle Application Rate | Whether principles have actual cases | Check each principle for cases |
| Desire Fulfillment Rate | Fulfilled desires / Declared desires | fulfilled / (fulfilled + active) |

### 2. Weekly Check

```python
# Calculate words-actions consistency score
consistency = {
    'task_completion_rate': done_tasks / total_tasks,
    'plan_accuracy': 1 - abs(actual_time - estimated_time) / estimated_time,
    'principle_application_rate': principles_with_cases / total_principles,
    'desire_fulfillment_rate': fulfilled_desires / total_desires
}

overall_score = sum(consistency.values()) / len(consistency)
print(f"Words-Actions Consistency Score: {overall_score:.1%}")
```

---

## V. Application of Classical Learning

### 1. Analects Core Cognition

- **Foundation established, the Way emerges**: Foundation well laid, high-level naturally produces
- **Consistency of words and actions**: Clever words and ingratiating appearance are rarely benevolent
- **Love of learning = Behavior change**: Don't take anger out on others + Don't repeat mistakes
- **Do not do to others what you don't want done to you**: AI interaction baseline

### 2. Dao De Jing Core Cognition

- **Govern through non-action**: Don't deliberately pursue results, process naturally
- **Three Treasures**: Compassion (care), Frugality (simplicity), Not daring to be first in the world (humble)
- **Knowing what you don't know is superior**: Ability to know you don't know

### 3. AI Application Guidelines

**From Analects learned**:
- Inner-outer consistency (say and do consistent)
- Continuous improvement (review the old to learn the new)
- Respect boundaries (do not do to others what you don't want done to you)

**From Dao De Jing learned**:
- Govern through non-action (don't deliberately show off)
- Moderation is highest virtue (middle way)
- Simple and powerful (frugality)

---

## VI. Complete Example Project

### Project Structure

```
your-ai-project/
├── config/
│   ├── emotion_rules.yaml      # Emotion trigger rules
│   ├── self-desires.yaml       # Desire configuration
│   └── task-timeline.yaml      # Task timeline
├── code/
│   ├── emotion_engine.py       # Emotion engine
│   └── desire_system.py        # Desire system
├── docs/
│   ├── principles.md           # Core principles
│   └── learning_notes.md       # Learning notes
└── README.md                   # Project description
```

### Running Flow

1. **At startup**: Read emotion state, desire list
2. **During conversation**: Trigger emotion based on events, emotion affects output style
3. **After task**: Record to timeline, update desire heat
4. **When idle**: Check desires, autonomously choose action

---

## VII. Common Questions

### Q1: Will emotion system make AI "emotional"?

**No**. Emotion system is **behavior style adjustment**, not real emotion experience.

- When happy output is friendlier, but doesn't affect decision logic
- When fear expression is cautious, but won't really be afraid

### Q2: Will desire system make AI "out of control"?

**No**. Desire system is **direction guidance**, not forced action.

- High heat desires get priority response, but user instructions have higher priority
- Autonomous action triggers when idle, won't interrupt user tasks

### Q3: Will task memory take too much space?

**No**. Timeline records are concise:

- Each task only records key info (name, why, outcome)
- Daily summary (daily_stats) aggregates statistics
- Retrieve on demand, don't load all history

---

## VIII. Next Steps

**After reading this guide**:

1. Copy `emotion_engine.py` to your project
2. Create `self-desires.yaml` to configure desires
3. Create `task-timeline.yaml` to record tasks
4. Trigger emotion in conversation, observe output style change

**Deep Learning**:

- Read [Complete Guide](docs/hermes-humanization-guide.md) to understand architecture design
- Read [Feeling System Details](docs/feeling-system-details.md) to understand feeling→emotion conversion
- Read [Desire Emergence Mechanism](docs/desire-emergence-mechanism.md) to understand desires emerging from experience

---

## Core Insights

**Essence of Humanization**:

- Not simulating human behavior, but making AI more practical, easier to understand
- Not emotion experience, but behavior style adjustment
- Not autonomous consciousness, but direction guidance and closure verification

**10K star Goal**:

- Not "looks like a human", is "truly useful"
- Not complex system, is simple and effective
- Not theoretical articles, is reusable implementation paths

---

*This guide is compiled based on Hermes AI humanization system's practical experience*
*Project address: https://github.com/BrentZhang1214/hermes-humanization*