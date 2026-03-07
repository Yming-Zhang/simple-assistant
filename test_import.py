import sys
from pathlib import Path

print("Python 路径:")
for p in sys.path:
    print(f"  {p}")

print("\n当前目录:")
print(f"  {Path.cwd()}")

print("\n项目根目录内容:")
project_root = Path(__file__).parent
print(f"  {project_root}")
print(f"  内容: {list(project_root.iterdir())}")

print("\n尝试导入...")
try:
    sys.path.insert(0, str(project_root))
    import config
    print("✓ 成功导入 config")
    
    from llm.base import LLMProvider
    print("✓ 成功导入 llm.base")
    
    from llm.response import ChatResponse
    print("✓ 成功导入 llm.response")
    
    print("\n✅ 所有导入成功！")
    
except Exception as e:
    print(f"\n❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
