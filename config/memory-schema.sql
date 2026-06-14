-- Hermes Humanization v0.2 记忆系统数据库架构
-- 7张核心表：events/backlog/desires/concepts/concept_links/event_concept_refs/reviews

-- 事件表：记录所有任务和行动
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    date TEXT,
    status TEXT CHECK(status IN ('done', 'in_progress', 'pending', 'cancelled')),
    type TEXT CHECK(type IN ('学习', '整理', '创作', '开发', '运维', '思考', '自主行动')),
    description TEXT,
    outcome TEXT,
    why TEXT,
    created TEXT,
    started TEXT,
    completed TEXT,
    duration_min REAL,
    time_actual REAL,
    experience_level TEXT CHECK(experience_level IN ('高', '中', '低')),
    value_assessment INTEGER CHECK(value_assessment BETWEEN 1 AND 10),
    context_source TEXT,
    context_trigger TEXT,
    steps TEXT,  -- JSON列表
    insights TEXT,  -- JSON列表
    files_created TEXT,  -- JSON列表
    files_modified TEXT,  -- JSON列表
    knowledge_file TEXT,
    distill_status TEXT CHECK(distill_status IN ('raw', 'distilled', 'expressed'))
);

-- 待办表：记录未完成的任务
CREATE TABLE IF NOT EXISTS backlog (
    id TEXT PRIMARY KEY,
    source_task TEXT,
    source_date TEXT,
    description TEXT,
    priority TEXT CHECK(priority IN ('high', 'medium', 'low')),
    status TEXT CHECK(status IN ('pending', 'in_progress', 'resolved')),
    created TEXT,
    updated TEXT,
    theme TEXT,
    interest INTEGER,
    note TEXT,
    resolution TEXT,
    files_created TEXT,  -- JSON列表
    files_verified TEXT  -- JSON列表
);

-- 欲望表：记录内在动机和目标
CREATE TABLE IF NOT EXISTS desires (
    id TEXT PRIMARY KEY,
    source TEXT,
    description TEXT,
    heat INTEGER CHECK(heat BETWEEN 0 AND 100),
    status TEXT CHECK(status IN ('active', 'cooling', 'partially_fulfilled', 'fulfilled')),
    created TEXT,
    fulfilled_date TEXT,
    fulfilled_note TEXT,
    goal TEXT,
    strategy TEXT,
    current_status TEXT,
    note TEXT
);

-- 概念表：记录所有知识概念
CREATE TABLE IF NOT EXISTS concepts (
    id TEXT PRIMARY KEY,
    name_zh TEXT,
    name_en TEXT,
    kind TEXT CHECK(kind IN ('concept', 'principle', 'method', 'model', 'observation', 'insight')),
    domain TEXT,
    definition TEXT,
    body TEXT,
    body_path TEXT,
    parent_id TEXT,
    confidence TEXT CHECK(confidence IN ('半懂', '掌握', '深刻')),
    importance TEXT CHECK(importance IN ('核心', '重要', '外围')),
    first_learned TEXT,
    last_reviewed TEXT,
    usage_count INTEGER DEFAULT 0,
    status TEXT CHECK(status IN ('active', 'deprecated', 'merged')),
    tags TEXT,  -- JSON列表
    created TEXT,
    updated TEXT
);

-- 概念关联表：记录概念之间的关系
CREATE TABLE IF NOT EXISTS concept_links (
    from_id TEXT,
    to_id TEXT,
    link_type TEXT CHECK(link_type IN ('is_a', 'part_of', 'derived_from', 'analogous_to', 'contradicts', 'applies_to', 'explains', 'other')),
    strength INTEGER CHECK(strength BETWEEN 1 AND 5),
    note TEXT,
    created TEXT,
    PRIMARY KEY (from_id, to_id, link_type)
);

-- 事件-概念关联表：记录任务和概念的关系
CREATE TABLE IF NOT EXISTS event_concept_refs (
    event_id TEXT,
    concept_id TEXT,
    role TEXT CHECK(role IN ('learned', 'used', 'questioned', 'created')),
    note TEXT,
    created TEXT,
    PRIMARY KEY (event_id, concept_id, role)
);

-- 复习表：间隔重复复习记录
CREATE TABLE IF NOT EXISTS reviews (
    path TEXT PRIMARY KEY,
    title TEXT,
    added_date TEXT,
    last_review TEXT,
    next_review TEXT,
    interval_days INTEGER,
    ef REAL,
    repetitions INTEGER,
    last_grade INTEGER,
    note TEXT
);
