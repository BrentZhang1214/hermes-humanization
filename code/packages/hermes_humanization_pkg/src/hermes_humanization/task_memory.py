"""
任务记忆系统模块
基于SQLite的时间轴+知识图谱任务记忆，支持多维度检索、概念关联
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import sqlite3
import os
from contextlib import contextmanager

@dataclass
class Task:
    """任务条目（兼容v0.1 API）"""
    id: str
    name: str
    created: datetime
    status: str = "pending"  # pending, in_progress, done, cancelled
    task_type: str = "general"
    why: str = ""
    time_actual: float = 0.0
    steps: List[str] = field(default_factory=list)
    outcome: str = ""
    insights: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)

class TaskMemory:
    """任务记忆系统 - 基于SQLite的时间轴+知识图谱记忆"""
    
    # 7张核心表结构（与本地memdb一致）
    _SCHEMA = {
        'events': [
            'id TEXT PRIMARY KEY',
            'date TEXT',
            'status TEXT CHECK(status IN (\'done\', \'in_progress\', \'pending\', \'cancelled\'))',
            'type TEXT CHECK(type IN (\'学习\', \'整理\', \'创作\', \'开发\', \'运维\', \'思考\', \'自主行动\'))',
            'description TEXT',
            'outcome TEXT',
            'why TEXT',
            'created TEXT',
            'started TEXT',
            'completed TEXT',
            'duration_min REAL',
            'time_actual REAL',
            'experience_level TEXT CHECK(experience_level IN (\'高\', \'中\', \'低\'))',
            'value_assessment INTEGER CHECK(value_assessment BETWEEN 1 AND 10)',
            'context_source TEXT',
            'context_trigger TEXT',
            'steps TEXT',  # JSON列表
            'insights TEXT',  # JSON列表
            'files_created TEXT',  # JSON列表
            'files_modified TEXT',  # JSON列表
            'knowledge_file TEXT',
            'distill_status TEXT CHECK(distill_status IN (\'raw\', \'distilled\', \'expressed\'))'
        ],
        'backlog': [
            'id TEXT PRIMARY KEY',
            'source_task TEXT',
            'source_date TEXT',
            'description TEXT',
            'priority TEXT CHECK(priority IN (\'high\', \'medium\', \'low\'))',
            'status TEXT CHECK(status IN (\'pending\', \'in_progress\', \'resolved\'))',
            'created TEXT',
            'updated TEXT',
            'theme TEXT',
            'interest INTEGER',
            'note TEXT',
            'resolution TEXT',
            'files_created TEXT',  # JSON列表
            'files_verified TEXT'  # JSON列表
        ],
        'desires': [
            'id TEXT PRIMARY KEY',
            'source TEXT',
            'description TEXT',
            'heat INTEGER CHECK(heat BETWEEN 0 AND 100)',
            'status TEXT CHECK(status IN (\'active\', \'cooling\', \'partially_fulfilled\', \'fulfilled\'))',
            'created TEXT',
            'fulfilled_date TEXT',
            'fulfilled_note TEXT',
            'goal TEXT',
            'strategy TEXT',
            'current_status TEXT',
            'note TEXT'
        ],
        'concepts': [
            'id TEXT PRIMARY KEY',
            'name_zh TEXT',
            'name_en TEXT',
            'kind TEXT CHECK(kind IN (\'concept\', \'principle\', \'method\', \'model\', \'observation\', \'insight\'))',
            'domain TEXT',
            'definition TEXT',
            'body TEXT',
            'body_path TEXT',
            'parent_id TEXT',
            'confidence TEXT CHECK(confidence IN (\'半懂\', \'掌握\', \'深刻\'))',
            'importance TEXT CHECK(importance IN (\'核心\', \'重要\', \'外围\'))',
            'first_learned TEXT',
            'last_reviewed TEXT',
            'usage_count INTEGER DEFAULT 0',
            'status TEXT CHECK(status IN (\'active\', \'deprecated\', \'merged\'))',
            'tags TEXT',  # JSON列表
            'created TEXT',
            'updated TEXT'
        ],
        'concept_links': [
            'from_id TEXT',
            'to_id TEXT',
            'link_type TEXT CHECK(link_type IN (\'is_a\', \'part_of\', \'derived_from\', \'analogous_to\', \'contradicts\', \'applies_to\', \'explains\', \'other\'))',
            'strength INTEGER CHECK(strength BETWEEN 1 AND 5)',
            'note TEXT',
            'created TEXT',
            'PRIMARY KEY (from_id, to_id, link_type)'
        ],
        'event_concept_refs': [
            'event_id TEXT',
            'concept_id TEXT',
            'role TEXT CHECK(role IN (\'learned\', \'used\', \'questioned\', \'created\'))',
            'note TEXT',
            'created TEXT',
            'PRIMARY KEY (event_id, concept_id, role)'
        ]
    }
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化任务记忆系统
        :param db_path: SQLite数据库路径，默认 ~/.hermes/memory.db
        """
        self.db_path = db_path or os.path.expanduser("~/.hermes/memory.db")
        self._init_db()

    def _init_db(self):
        """初始化数据库表（不存在则创建）"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._connect() as conn:
            cursor = conn.cursor()
            for table, columns in self._SCHEMA.items():
                create_sql = f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(columns)})"
                cursor.execute(create_sql)
            conn.commit()
    
    @contextmanager
    def _connect(self, commit: bool = True, row_factory: bool = True):
        """数据库连接上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        if row_factory:
            conn.row_factory = sqlite3.Row
        try:
            yield conn
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _now(self) -> str:
        """统一时间戳格式 YYYY-MM-DD HH:MM:SS"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _today(self) -> str:
        """统一日期格式 YYYY-MM-DD"""
        return datetime.now().strftime('%Y-%m-%d')
    
    def next_id(self, table: str, prefix: Optional[str] = None) -> str:
        """
        生成下一个可用ID
        :param table: 表名（events/backlog/desires/concepts）
        :param prefix: 可选前缀，默认events用日期前缀，backlog用B，desires用D，concepts用C
        """
        if table == 'events':
            date = self._today()
            with self._connect(commit=False) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM events WHERE id LIKE ? ORDER BY id DESC LIMIT 1", (f"{date}-T%",))
                row = cursor.fetchone()
                if not row:
                    return f"{date}-T001"
                num = int(row['id'].rsplit('-T', 1)[1]) + 1
                return f"{date}-T{num:03d}"
        
        default_prefix = {'backlog': 'B', 'desires': 'D', 'concepts': 'C'}
        prefix = prefix or default_prefix.get(table, 'X')
        with self._connect(commit=False) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT id FROM {table} WHERE id LIKE ? ORDER BY id DESC LIMIT 1", (f"{prefix}%",))
            row = cursor.fetchone()
            if not row:
                return f"{prefix}001"
            num = int(row['id'][len(prefix):]) + 1
            return f"{prefix}{num:03d}"

    # ========== v0.1 兼容API ==========
    def add_task(self, name: str, task_type: str = "general", why: str = "") -> Task:
        """
        添加新任务（兼容v0.1 API）
        """
        task_id = self.next_id('events')
        task = Task(
            id=task_id,
            name=name,
            created=datetime.now(),
            task_type=task_type,
            why=why
        )
        # 自动写入events表
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (id, date, status, type, description, why, created)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id,
                self._today(),
                'pending',
                '开发' if task_type == '技术实现' else task_type,
                name,
                why,
                self._now()
            ))
        return task
    
    def _save(self):
        """兼容v0.1 API（空实现，SQLite自动持久化）"""
        pass
    
    def get_recent_tasks(self, limit: int = 10) -> List[Task]:
        """
        获取最近任务（兼容v0.1 API）
        """
        with self._connect(commit=False) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, description, created, status, type, why, time_actual,
                       steps, outcome, insights, files_created, files_modified
                FROM events
                ORDER BY created DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
        
        tasks = []
        for row in rows:
            task = Task(
                id=row['id'],
                name=row['description'],
                created=datetime.strptime(row['created'], '%Y-%m-%d %H:%M:%S'),
                status=row['status'],
                task_type=row['type'],
                why=row['why'],
                time_actual=row['time_actual'] or 0.0,
                steps=eval(row['steps'] or '[]'),
                outcome=row['outcome'] or '',
                insights=eval(row['insights'] or '[]'),
                files_created=eval(row['files_created'] or '[]'),
                files_modified=eval(row['files_modified'] or '[]')
            )
            tasks.append(task)
        return tasks
    
    def search_by_keyword(self, keyword: str) -> List[Task]:
        """
        按关键词搜索任务（兼容v0.1 API）
        """
        keyword = f"%{keyword.lower()}%"
        with self._connect(commit=False) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, description, created, status, type, why, time_actual,
                       steps, outcome, insights, files_created, files_modified
                FROM events
                WHERE LOWER(description) LIKE ? OR LOWER(why) LIKE ? OR LOWER(outcome) LIKE ? OR LOWER(insights) LIKE ?
                ORDER BY created DESC
            """, (keyword, keyword, keyword, keyword))
            rows = cursor.fetchall()
        
        tasks = []
        for row in rows:
            task = Task(
                id=row['id'],
                name=row['description'],
                created=datetime.strptime(row['created'], '%Y-%m-%d %H:%M:%S'),
                status=row['status'],
                task_type=row['type'],
                why=row['why'],
                time_actual=row['time_actual'] or 0.0,
                steps=eval(row['steps'] or '[]'),
                outcome=row['outcome'] or '',
                insights=eval(row['insights'] or '[]'),
                files_created=eval(row['files_created'] or '[]'),
                files_modified=eval(row['files_modified'] or '[]')
            )
            tasks.append(task)
        return tasks

    # ========== v0.2 新增API ==========
    def record_event(self, event_data: Dict) -> str:
        """
        记录完整事件
        :param event_data: 事件字典，包含events表字段
        """
        event_id = event_data.get('id') or self.next_id('events')
        event_data['id'] = event_id
        event_data['date'] = event_data.get('date') or self._today()
        event_data['created'] = event_data.get('created') or self._now()
        event_data['status'] = event_data.get('status') or 'done'
        
        # 提取字段
        columns = [col.split(' ')[0] for col in self._SCHEMA['events']]
        values = []
        placeholders = []
        for col in columns:
            if col in event_data:
                val = event_data[col]
                if isinstance(val, list):
                    val = repr(val)
                values.append(val)
                placeholders.append('?')
            else:
                placeholders.append('NULL')
        
        with self._connect() as conn:
            cursor = conn.cursor()
            sql = f"INSERT INTO events ({','.join(columns)}) VALUES ({','.join(placeholders)})"
            cursor.execute(sql, values)
        return event_id
    
    def add_concept(self, concept_data: Dict) -> str:
        """添加新概念"""
        concept_id = concept_data.get('id') or self.next_id('concepts')
        concept_data['id'] = concept_id
        concept_data['created'] = concept_data.get('created') or self._now()
        
        columns = [col.split(' ')[0] for col in self._SCHEMA['concepts']]
        values = []
        placeholders = []
        for col in columns:
            if col in concept_data:
                val = concept_data[col]
                if isinstance(val, list):
                    val = repr(val)
                values.append(val)
                placeholders.append('?')
            else:
                placeholders.append('NULL')
        
        with self._connect() as conn:
            cursor = conn.cursor()
            sql = f"INSERT INTO concepts ({','.join(columns)}) VALUES ({','.join(placeholders)})"
            cursor.execute(sql, values)
        return concept_id
    
    def link_concepts(self, from_id: str, to_id: str, link_type: str = 'related', strength: int = 3, note: str = ''):
        """关联两个概念"""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO concept_links (from_id, to_id, link_type, strength, note, created)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (from_id, to_id, link_type, strength, note, self._now()))
    
    def get_concept_graph(self, root_concept_id: str, max_depth: int = 2) -> Dict:
        """获取概念图谱"""
        graph = {'nodes': [], 'edges': []}
        visited = set()
        
        def dfs(node_id, depth):
            if depth > max_depth or node_id in visited:
                return
            visited.add(node_id)
            
            # 获取节点信息
            with self._connect(commit=False) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name_zh, name_en, kind FROM concepts WHERE id = ?", (node_id,))
                node = cursor.fetchone()
                if node:
                    graph['nodes'].append(dict(node))
                
                # 获取出边
                cursor.execute("""
                    SELECT from_id, to_id, link_type, strength
                    FROM concept_links
                    WHERE from_id = ?
                """, (node_id,))
                edges = cursor.fetchall()
                for edge in edges:
                    graph['edges'].append(dict(edge))
                    dfs(edge['to_id'], depth + 1)
        
        dfs(root_concept_id, 0)
        return graph
    
    def get_event_concepts(self, event_id: str) -> List[Dict]:
        """获取事件关联的所有概念"""
        with self._connect(commit=False) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, ecr.role
                FROM event_concept_refs ecr
                JOIN concepts c ON ecr.concept_id = c.id
                WHERE ecr.event_id = ?
            """, (event_id,))
            return [dict(row) for row in cursor.fetchall()]
