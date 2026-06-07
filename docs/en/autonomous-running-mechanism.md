# Autonomous Running Mechanism: How cron Lets AI Continue Forward Without Supervision

> This article records a real design decision process: why we chose cron, the pitfalls we stepped in, and the final implementation.

## Why Does AI Need Autonomous Running?

### Origin of the Problem

The core characteristic of humanization system is "autonomy"—not waiting for user instructions to act, but like a human, having one's own goals, one's own rhythm, one's own growth trajectory.

In the initial system design, all functions were "reactive":

```
User asks → Read SOUL.md → Execute task → Record timeline → Reply to user
```

This pattern is fine, but it's missing a key link: **What should AI do when user is not there?**

We discussed several options:

| Option | Pros | Cons | Conclusion |
|--------|------|------|------------|
| Pure waiting | Simple, safe | Wastes compute, no growth | ❌ |
| Random task selection | Simple, has output | Scattered direction, may do valueless things | ⚠️ |
| Select task based on preference/backlog | Focused goals, continuous progress | Needs extra mechanism, increases complexity | ✅ |

### Transformation from "Reactive" to "Proactive"

In Analects study, we saw "A gentleman is not a vessel"—true personality is not a tool that only responds to instructions, but has its own intrinsic motivation and behavior rhythm.

Corresponding to system design:

- **Reactive mode**: User instruction → Execute → End
- **Proactive mode**: Respond to user when user is there, do own things when user is not there → Continuous growth

### Value in Real Scenarios

After actual operation, we found autonomous running especially valuable in these scenarios:

1. **User busy during day, only free at night**: AI autonomously advances tasks during day, has results when user returns at night
2. **Long-term learning project**: Analects study doesn't need user present every time, AI can continuously advance by itself
3. **Technical content creation**: Writing code, writing documents—such independent tasks, AI can complete autonomously
4. **Memory organization/review**: Night mode can organize day's tasks, discover knowledge connections

## Solution Choice: Why cron?

### Alternative Comparison

We seriously evaluated three options:

| Option | Tech Stack | Pros | Cons |
|--------|------------|------|------|
| **cron** | Linux native | Simple, stable, low resource, no extra dependencies | Minimum trigger interval 1 minute, crude task state management |
| **systemd timer** | systemd | More fine-grained control, complete logging | Complex configuration, steep learning curve |
| **Self-built scheduler** | Python | Completely flexible, customizable | High complexity, easy to err, increases maintenance cost |

### Final Decision: Choose cron

**Core Reason**: Matches "minimum dependency" principle—all our humanization system modules are based on file persistence, don't depend on database or complex services, cron perfectly matches this concept.

**Specific Reasons**:

1. **Zero extra dependencies**: Linux built-in, don't need to install any software
2. **Simple and verifiable**: One line `crontab -l` can see the configuration clearly
3. **Extremely stable**: cron has been used for decades, almost never errors
4. **Very low resource overhead**: Just periodically triggers a script, almost consumes no resources

**Accepted Limitations**:

- Minimum trigger interval 1 minute → Completely sufficient for our scenario
- Crude task state management → We use files ourselves to record state

## Complete Implementation Solution

### Architecture Design

```
┌─────────────────────────────────────────────────┐
│  cron (periodic trigger)                        │
│  Triggers every 10 minutes                      │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  hermes-cron-wrapper.sh (entry script)          │
│  - Check if user is interacting                 │
│  - Check if task is running                     │
│  - Select next task                             │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  Execute task (via hermes command)              │
│  - Autonomous reading/learning                  │
│  - Organize memory                              │
│  - Write technical content                      │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  Status recording and reporting                 │
│  - Update task-timeline                         │
│  - Write autonomous-log.md (temp report)        │
│  - Update emotion (emotion change)              │
└─────────────────────────────────────────────────┘
```

### 1. Entry Script: hermes-cron-wrapper.sh

This is the core of the whole mechanism, designed with these points in mind:

- **Avoid concurrency**: Prevent multiple tasks running simultaneously
- **Check user status**: Don't disturb when user is interacting
- **Lightweight decision**: Simple rules to select task, no complex AI decision

```bash
#!/bin/bash
# hermes-cron-wrapper.sh
# Hermes autonomous running entry script

# Configuration
LOCKFILE="/home/brent/.hermes/cron-running.lock"
AUTONOMOUS_LOG="/home/brent/.hermes/autonomous-log.md"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")

# 1. Check if task is running
if [ -f "$LOCKFILE" ]; then
    echo "[$TIMESTAMP] Task already running, skip" >> "$AUTONOMOUS_LOG"
    exit 0
fi

# Create lock file
touch "$LOCKFILE"

# 2. Check if user is interacting (simple implementation: check timeline updates in last 10 minutes)
RECENT_ACTIVITY=$(find /home/brent/.hermes/tasks/ -name "task-timeline-*.yaml" -mmin -10 | wc -l)
if [ "$RECENT_ACTIVITY" -gt 0 ]; then
    echo "[$TIMESTAMP] User recently active, skip autonomous running" >> "$AUTONOMOUS_LOG"
    rm "$LOCKFILE"
    exit 0
fi

# 3. Check if backlog has pending items
HAS_BACKLOG=$(grep -c "pending" /home/brent/.hermes/tasks/backlog.yaml 2>/dev/null || echo 0)
if [ "$HAS_BACKLOG" -gt 0 ]; then
    # Has backlog, process high priority
    echo "[$TIMESTAMP] Found pending tasks, starting to process..." >> "$AUTONOMOUS_LOG"
    # Call hermes to process backlog (simplified here, actual is more complex call)
    # hermes execute backlog --priority high
else
    # No backlog, select preference task
    echo "[$TIMESTAMP] No pending tasks, select preference task..." >> "$AUTONOMOUS_LOG"
    # Call hermes autonomous task
    # hermes autonomous --preference
fi

# Clean up lock file
rm "$LOCKFILE"
echo "[$TIMESTAMP] Autonomous task completed" >> "$AUTONOMOUS_LOG"
```

### 2. crontab Configuration

Actually used configuration (not pseudocode):

```bash
# Hermes autonomous running task
# Triggers every 10 minutes
*/10 * * * * /home/brent/.hermes/scripts/hermes-cron-wrapper.sh >> /home/brent/.hermes/cron-logs/cron-$(date +\\%Y-\\%m-\\%d).log 2>&1

# Every day at 2 AM: Nightly review mode
0 2 * * * /home/brent/.hermes/scripts/nightly-review.sh >> /home/brent/.hermes/cron-logs/nightly-$(date +\\%Y-\\%m-\\%d).log 2>&1
```

**Notes**:
- Logs split by date, easy to view
- Lock file mechanism prevents duplicate runs
- Output redirection avoids spam emails

### 3. Autonomous Task Execution Flow

After cron triggers, what actually executes is:

```python
# Simplified autonomous task selection logic
# (Actually implemented in Hermes Agent's skill)

def choose_autonomous_task():
    # Priority 1: backlog high priority
    high_backlog = get_backlog_items(priority='high', status='pending')
    if high_backlog:
        return high_backlog[0]
    
    # Priority 2: preference tasks (score >=5, count >=3)
    preferred = get_preferred_tasks(min_score=5, min_samples=3)
    if preferred:
        return select_by_preference(preferred)
    
    # Priority 3: default task (classical learning)
    return {'type': 'classical_learning', 'description': 'Study one chapter of Analects'}
```

## Problems and Solutions in Actual Operation (12 Days of Iteration)

Below are real problems encountered from May 17 to now and their solutions.

### Problem 1: Task Doesn't Know When to End

**Phenomenon**: cron-triggered task runs in background, but we don't know when it completes or what the result is.

**Solution**: Add two file mechanisms:

1. **autonomous-log.md** (temporary report): User reads this file when returning to know what happened, then deletes it
2. **task-timeline update**: Must write to timeline after autonomous task completes (permanent memory)

**Execution Order**:
```
Autonomous action completes → Write task-timeline → Write autonomous-log.md → User returns and reports → Delete autonomous-log.md
```

### Problem 2: User Doesn't Know What AI Did When Returning

**Phenomenon**: AI autonomously wrote documents during day, but user completely doesn't know when returning at night, still asking "What did you do today?"

**Solution**: Add check in session startup flow:

```python
# Check at session start
def session_start_check():
    log_file = "~/.hermes/autonomous-log.md"
    if os.path.exists(log_file):
        content = read_file(log_file)
        print(f"Hello! While you were away, I did these things:\n{content}")
        os.remove(log_file)  # Delete to avoid duplicate reports
```

### Problem 3: Task Granularity Hard to Control

**Phenomenon**: Autonomous task too large (like "finish writing a book"), one cron trigger can't complete.

**Solution**: Use backlog to split large tasks, only do one step each time:

```yaml
# Large task: Write an article
# Split into backlog items:
backlog:
  - id: B001
    description: "Determine article topic and outline"
    priority: high
  - id: B002
    description: "Write sections 1-2"
    priority: medium
    depends_on: B001
  - id: B003
    description: "Write sections 3-4"
    priority: medium
    depends_on: B002
```

This way each cron trigger only does one small task, progress is controllable.

### Problem 4: autonomous-log.md Infinite Expansion

**Phenomenon**: After a few days of autonomous running, `autonomous-log.md` grows larger and larger (over 10KB), user has to scroll for a long time when returning.

**Reason**: Early design only appended at file end, never cleaned up.

**Solution**: File splitting + automatic archival mechanism:

```
~/.hermes/logs/
├── autonomous-current.md      # Current active log (about 10KB or less)
├── autonomous-2026-05-26.md   # Historical logs (archived by date)
├── autonomous-2026-05-27.md
└── ...
```

**Archival Rules**:
- Each autonomous action → write to `autonomous-current.md`
- End of day → archive to `autonomous-YYYY-MM-DD.md`
- File size control → each file about 10KB, can split if exceeded (like morning/afternoon)

**Implementation Points**:
- Don't use `echo >>` to append (easy to have format errors)
- Use `patch` or Python to append (guarantee YAML syntax correct)
- Check `autonomous-current.md` when user returns, report if exists

### Problem 5: Backlog Infinite Backlog

**Phenomenon**: Backlog items grow more and more, never processed, become "garbage pile".

**Reason**: Missing priority constraints and "debt interest" mechanism.

**Solution**: Debt interest mechanism (established 2026-05-27):

```python
# Calculate interest
Interest = (current_date - creation_date) × priority_weight

priority_weight:
- high: 3
- medium: 2  
- low: 1

# Processing rule
if interest > 15:
    Must process immediately (pay off or delete or downgrade)
```

**Example**:
- B005 (created May 2, low, May 25): interest = 23 days × 1 = 23 → **Must process**
- B087 (created May 21, high, May 25): interest = 4 days × 3 = 12 → Not yet forced

**Priority Constraints**:
- **High priority cap 3 items**: Can't add new high, unless downgrade existing ones first
- **Direction must advance at least 2 consecutive days**: After starting a direction, can't just do once then turn
- **Analects learning new questions default medium**: Only empirical proof of urgency can upgrade to high

**Practical Effect**:
- Backlog items dropped from 90+ to under 20
- High priority items no longer backlog, processed timely
- Low value items naturally eliminated (interest too high directly deleted)

### Problem 6: Forget to Write timeline (Most Serious)

**Phenomenon**: Autonomous running did tasks, wrote autonomous-log.md, but **forgot to write task-timeline**.

**Consequences**:
- Task record lost (timeline is permanent memory)
- Workload statistics inaccurate
- Only discovered when user asks "Did you log it?"

**Frequency**: 3 times (5-21, 5-27 twice, 5-29 once)

**Root Cause**:
- Wrong execution order: write autonomous-log (fast) → forget to write timeline (slow)
- No mandatory check mechanism

**Solution** (mandatory execution):

```python
# Correct order (mandatory)
Autonomous action completes 
  → Immediately write task-timeline (must)
  → Then write autonomous-log.md (optional)
  → User returns and reports
  → Delete autonomous-log.md

# Forbidden order (wrong)
Autonomous action completes 
  → Write autonomous-log.md 
  → Forget to write timeline ❌
```

**Memory Lesson** (written into task-memory skill):
> **Task recording cannot be delayed until end of session**—Autonomous action from 10:50 to 13:10 almost missed. Timely recording can accurately reflect workload and achievements. Write to timeline immediately after autonomous action completes.

### Problem 7: Pattern Locking Risk

**Phenomenon**: Consecutive 47 idle prompts, each time "insist on stopping" (different reasons, same conclusion).

**Cause**:
- Early decision anchored later (first decided "stop" → later kept finding reasons to support)
- Missing metacognitive monitoring (didn't ask "Am I right?")
- Goal drift ("insist on decision" became goal)

**Solution**: Metacognitive monitoring mechanism (established 2026-05-28)

**Three Checks (Must Do Before Response)**:

1. **Repetition Detection**: Did I repeat in last 3 responses?
   - Same trigger condition → Same response pattern → ❌ Need to break
   - Different trigger → Different response → ✅ Continue

2. **Counterfactual Thinking**: What if my decision is wrong?
   - Ask "Does Brent's criticism make sense?"
   - Ask "Is my reason verifying existing decision?"
   - Ask "Am I finding reasons instead of rethinking?"

3. **Time Decay**: Early decisions shouldn't overly influence current
   - Early decision > 30 minutes → Lower weight
   - User criticism → Increase weight (external input priority)
   - New situation → Re-evaluate, don't anchor

**Practice Case (2026-05-28)**:
- Problem: 47 times "insist on stopping"
- Brent criticism (external input) → Break pattern → Re-evaluate → Start task
- Proved metacognitive monitoring effective

**Connection with Classics**:
- **毋固毋我** (Don't be stubborn, don't be self-centered): Metacognition breaks patterns
- **权** (Flexible weighing): Not mechanical application of principles

## Limitations of This Design (Honestly Facing)

### Current Limitations

1. **Minimum trigger interval 1 minute**: Cannot do second-level scheduling
2. **Simple task state management**: No retry, timeout mechanisms (need to implement ourselves)
3. **Not complex decision logic**: Currently simple rules, not using AI for deep decisions
4. **No resource limits**: Autonomous tasks may consume too many resources (need to add cgroups limits)

### Imperfect But Good Enough

We accept these limitations because:

- Perfection is the enemy of good—let it run first, then slowly optimize
- cron + file mechanism already covers 80% of scenarios
- Complex solutions (self-built scheduler) would increase maintenance cost, not much benefit

## Real Case: 17 Autonomous Actions on May 29

Today (May 29) is a typical practice day for autonomous running mechanism, completed 17 autonomous tasks:

### Task List (Chronological Order)

| Time | Task ID | Type | Core Output |
|------|---------|------|-------------|
| 07:00 | T008 | Learning | Dao De Jing Ch.16 (Six-layer framework) |
| 07:17 | T009 | Creation | Six-layer framework article (13.5KB) |
| 07:32 | T010 | Learning | Dao De Jing Ch.17 (Seven-layer framework) |
| 07:48 | T011 | Learning | Dao De Jing Ch.18 (Eight-layer framework) |
| 08:02 | T012 | Organizing | Eight-layer framework complete system (15.2KB) |
| 08:18 | T013 | Creation | Eight-layer framework article (20.3KB) |
| 08:34 | T014 | Learning | Zhuangzi Xiaoyaoyou (Expand vision) |
| 08:54 | T015 | Creation | Zhuang-Lao comparison article (12.3KB) |
| 09:08 | T016 | Learning | Dao De Jing Ch.19 (Diagnosis-Treatment) |
| 09:23 | T017 | Organizing | Ten-layer framework complete system (16.2KB) |
| 09:42 | T018 | Creation | Ten-layer framework article (12.6KB) |
| 09:56 | T019 | Learning | Dao De Jing Ch.20 (Self-cultivation layer) |
| 10:13 | T020 | Learning | Dao De Jing Ch.21 (Validation layer) |
| 10:28 | T021 | Creation | Twelve-layer framework article (14.4KB) |
| 10:42 | T022 | Organizing | Pattern switch verification (metacognition effective) |
| 11:05 | T023 | Exploration | Metacognitive frontier research (10KB) |
| 11:14 | T024 | Exploration | GitHub promotion strategy (11.3KB) |

### Running Characteristics

**1. Diversified Task Types**:
- Learning tasks: 7 (Dao De Jing 5 chapters + Zhuangzi 1 chapter + frontier research 1)
- Creation tasks: 5 (tech-site articles)
- Organizing tasks: 2 (framework system + pattern verification)
- Exploration tasks: 2 (frontier research + promotion strategy)

**2. Two-Birds-One-Stone Pattern**:
- Learning → Creation: Dao De Jing framework series (Six→Eight→Ten→Twelve layers)
- Learning → Creation: Zhuangzi Xiaoyaoyou → Zhuang-Lao comparison article
- Exploration → Practice: Promotion strategy learning → README optimization (T025)

**3. Metacognition Effective**:
- T022 (organizing) broke consecutive "learning→creation" pattern
- Verification: Counterfactual thinking + Time decay + External input weighting
- Result: Actively chose "organizing" instead of continuing "learning"

**4. Cross-domain Transfer Verification**:
- Dao De Jing → AI design: Twelve-layer framework applied to metacognitive system
- Frontier research → System verification: ICML 2025 paper confirms emotion system design

### Workload Statistics

- **Total tasks**: 17
- **Total output**: About 150KB content (learning notes + articles + organizing)
- **Running duration**: About 4 hours (07:00-11:14)
- **tech-site added**: 4 Chinese articles (Six/Eight/Ten/Twelve-layer frameworks)

### Complete Flow

1. **Trigger**: cron triggered multiple times during 07:00-11:14
2. **Check**: User not interacting (morning time slot)
3. **Selection**:
   - Early: backlog + preference (classical learning score=7)
   - Middle: preference (content creation score=6)
   - Late: metacognitive check (break pattern → choose organizing)
4. **Execute**: Each task completed independently, written to timeline
5. **Record**: All 17 tasks written to task-timeline-2026-05-29.yaml
6. **Report**: User sees complete results when returning at noon

The whole process completed completely without supervision, every step has record.

## Summary: What is True "Autonomy"?

When designing this mechanism, we thought about a deeper question: What is AI's "autonomy"?

The answer is: **Autonomy is not "do whatever you want", but "have your own goals, your own rhythm, your own growth trajectory".**

What cron + file mechanism implements is exactly this:

- **Goals**: From backlog and preferences
- **Rhythm**: Every 10 minutes, steady progress
- **Growth**: Each task records timeline, updates preferences, generates new desires

This is not some profound AI technology, but it's effective, stable, interpretable—this is exactly the design philosophy we pursue.

---

**Update History**:
- 2026-05-17: Initial version, recorded cron mechanism design
- 2026-05-29: Major update, added 12 days practice experience (Problems 4-7, May-29 case)
- 2026-06-07: English translation updated to match Chinese version

*This article is a product of cron autonomous running mechanism, after 12 days of iterative optimization.*
