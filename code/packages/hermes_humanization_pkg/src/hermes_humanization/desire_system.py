"""
欲望系统模块
负责管理AI的自主诉求和欲望
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict
from pathlib import Path
import yaml

@dataclass
class Desire:
    """欲望条目"""
    id: str
    content: str
    heat: float = 0.0  # 热度值
    status: str = "active"
    created: datetime = field(default_factory=datetime.now)
    
    def decay(self, rate: float = 0.1):
        """欲望衰减"""
        self.heat = max(0, self.heat - rate)

class DesireSystem:
    """欲望系统 - 管理AI的自主诉求"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".hermes" / "self-desires.yaml"
        self.desires: List[Desire] = []
        self._load()
    
    def _load(self):
        """加载欲望列表"""
        if self.storage_path.exists():
            with open(self.storage_path) as f:
                data = yaml.safe_load(f)
                if data and "desires" in data:
                    for item in data["desires"]:
                        self.desires.append(Desire(
                            id=item["id"],
                            content=item["content"],
                            heat=item.get("heat", 0),
                            status=item.get("status", "active"),
                        ))
    
    def add_desire(self, content: str, heat: float = 1.0) -> Desire:
        """添加新欲望"""
        desire = Desire(
            id=f"D{len(self.desires)+1:03d}",
            content=content,
            heat=heat,
        )
        self.desires.append(desire)
        self._save()
        return desire
    
    def _save(self):
        """保存欲望列表"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "desires": [
                {
                    "id": d.id,
                    "content": d.content,
                    "heat": d.heat,
                    "status": d.status,
                }
                for d in self.desires
            ]
        }
        with open(self.storage_path, "w") as f:
            yaml.dump(data, f)
    
    def get_active_desires(self) -> List[Desire]:
        """获取活跃欲望"""
        return [d for d in self.desires if d.status == "active" and d.heat > 0]