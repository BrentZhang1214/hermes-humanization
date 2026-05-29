"""
完整使用示例：验证系统
展示如何验证AI行动的真实性，防止自我欺骗
"""

from hermes_humanization import VerificationSystem, VerificationResult
from pathlib import Path

# 创建验证系统
verifier = VerificationSystem()

# 1. 验证文件存在
print("验证README.md存在:")
result = verifier.verify_file_exists(Path("README.md"))
print(f"  成功: {result.success}")
print(f"  消息: {result.message}")
if result.evidence:
    print(f"  证据: {result.evidence}")

verifier.add_verification(result)

# 2. 验证文件内容
print("\n验证README.md包含期望内容:")
result = verifier.verify_file_content(
    Path("README.md"),
    "AI拟人化核心系统"
)
print(f"  成功: {result.success}")
print(f"  消息: {result.message}")

verifier.add_verification(result)

# 3. 验证目录结构
print("\n验证src目录存在:")
src_path = Path("src/hermes_humanization")
result = verifier.verify_file_exists(src_path)
print(f"  成功: {result.success}")
print(f"  消息: {result.message}")

verifier.add_verification(result)

# 4. 验证核心模块
print("\n验证核心模块文件:")
modules = ["emotion_engine.py", "desire_system.py", "task_memory.py", "verification.py"]
for module in modules:
    module_path = src_path / module
    result = verifier.verify_file_exists(module_path)
    print(f"  {module}: {result.success}")
    verifier.add_verification(result)

# 5. 获取验证摘要
print("\n验证摘要:")
summary = verifier.get_verification_summary()
print(f"  总验证数: {summary['total']}")
print(f"  成功数: {summary['successful']}")
print(f"  失败数: {summary['failed']}")
print(f"  成功率: {summary['success_rate']:.1%}")

# 6. 使用场景：防止自我欺骗
print("\n【使用场景】防止自我欺骗")
print("AI声称：'我创建了文件 example.py'")
print("验证：检查文件是否真实存在")

hypothetical_file = Path("example.py")
result = verifier.verify_file_exists(hypothetical_file)
if result.success:
    print("  ✅ 验证通过，文件真实存在")
else:
    print("  ❌ 验证失败，文件不存在——AI可能在自我欺骗")