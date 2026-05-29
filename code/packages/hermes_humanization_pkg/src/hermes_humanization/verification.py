"""
验证系统模块
用于验证AI行动的真实性，防止自我欺骗
"""

from dataclasses import dataclass
from typing import Callable, Any, Optional
from pathlib import Path

@dataclass
class VerificationResult:
    """验证结果"""
    success: bool
    message: str
    evidence: Optional[str] = None

class VerificationSystem:
    """验证系统 - 确保AI行动真实有效"""
    
    def __init__(self):
        self.verifications = []
    
    def verify_file_exists(self, file_path: Path) -> VerificationResult:
        """验证文件是否存在"""
        if file_path.exists():
            return VerificationResult(
                success=True,
                message=f"文件存在: {file_path}",
                evidence=str(file_path.stat())
            )
        return VerificationResult(
            success=False,
            message=f"文件不存在: {file_path}"
        )
    
    def verify_file_content(self, file_path: Path, expected_content: str) -> VerificationResult:
        """验证文件内容包含期望文本"""
        if not file_path.exists():
            return VerificationResult(
                success=False,
                message=f"文件不存在: {file_path}"
            )
        
        content = file_path.read_text()
        if expected_content in content:
            return VerificationResult(
                success=True,
                message=f"文件包含期望内容: {expected_content[:50]}...",
                evidence=f"文件大小: {len(content)} 字符"
            )
        return VerificationResult(
            success=False,
            message=f"文件不包含期望内容: {expected_content[:50]}..."
        )
    
    def verify_command_output(
        self, 
        command: str, 
        checker: Callable[[str], bool],
        timeout: int = 30
    ) -> VerificationResult:
        """验证命令输出（需配合terminal工具）"""
        # 这个方法需要在Hermes Agent环境中使用terminal工具
        return VerificationResult(
            success=False,
            message="需要在Hermes Agent环境中实现"
        )
    
    def verify_git_commit(self, commit_hash: str) -> VerificationResult:
        """验证Git提交是否存在"""
        # 需要在Git仓库环境中实现
        return VerificationResult(
            success=False,
            message="需要在Git仓库环境中实现"
        )
    
    def add_verification(self, verification: VerificationResult):
        """记录验证结果"""
        self.verifications.append(verification)
    
    def get_verification_summary(self) -> dict:
        """获取验证摘要"""
        total = len(self.verifications)
        successful = sum(1 for v in self.verifications if v.success)
        return {
            "total": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total if total > 0 else 0,
        }