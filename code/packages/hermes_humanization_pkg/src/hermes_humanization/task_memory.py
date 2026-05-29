"""
任务记忆系统模块
基于时间轴的任务记录，支持多维度检索
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import yaml

@dataclass
class Task:
    """任务条目"""
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
    """任务记忆系统 - 基于时间轴的任务记录"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".hermes" / "tasks"
        self.tasks: List[Task] = []
        self._load_today()
    
    def _load_today(self):
        """加载今天的任务"""
        today = datetime.now().strftime("%Y-%m-%d")
        timeline_file = self.storage_path / f"task-timeline-{today}.yaml"
        
        if timeline_file.exists():
            with open(timeline_file) as f:
                data = yaml.safe_load(f)
                if data and "tasks" in data:
                    for item in data["tasks"]:
                        self.tasks.append(Task(
                            id=item["id"],
                            name=item["name"],
                            created=datetime.now(),  # 简化处理
                            status=item.get("status", "done"),
                            task_type=item.get("type", "general"),
                            why=item.get("why", ""),
                            time_actual=item.get("time_actual", 0),
                            steps=item.get("steps", []),
                            outcome=item.get("outcome", ""),
                            insights=item.get("insights", []),
                            files_created=item.get("files_created", []),
                            files_modified=item.get("files_modified", []),
                        ))
    
    def add_task(self, name: str, task_type: str = "general", why: str = "") -> Task:
        """添加新任务"""
        task_id = f"T{len(self.tasks)+1:03d}"
        task = Task(
            id=task_id,
            name=name,
            created=datetime.now(),
            task_type=task_type,
            why=why,
        )
        self.tasks.append(task)
        self._save()
        return task
    
    def _save(self):
        """保存任务列表"""
        today = datetime.now().strftime("%Y-%m-%d")
        timeline_file = self.storage_path / f"task-timeline-{today}.yaml"
        timeline_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "tasks": [
                {
                    "id": t.id,
                    "name": t.name,
                    "created": t.created.strftime("%H:%M"),
                    "status": t.status,
                    "type": t.task_type,
                    "why": t.why,
                    "time_actual": t.time_actual,
                    "steps": t.steps,
                    "outcome": t.outcome,
                    "insights": t.insights,
                    "files_created": t.files_created,
                    "files_modified": t.files_modified,
                }
                for t in self.tasks
            ]
        }
        
        with open(timeline_file, "w") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    
    def get_recent_tasks(self, limit: int = 10) -> List[Task]:
        """获取最近任务"""
        return sorted(self.tasks, key=lambda t: t.created, reverse=True)[:limit]
    
    def search_by_keyword(self, keyword: str) -> List[Task]:
        """按关键词搜索任务"""
        return [
            t for t in self.tasks
            if keyword.lower() in t.name.lower() or keyword.lower() in t.why.lower()
        ]