"""检查user_profiles的数据结构"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.connection import get_database

db = get_database()
profiles = db['user_profiles']

# 查看第一条数据
doc = profiles.find_one()
print("Profile结构:")
print(f"_id: {doc.get('_id')}")
print(f"Keys: {list(doc.keys())}")

if 'basic_info' in doc:
    print(f"\nbasic_info: {doc['basic_info']}")
else:
    print("\n没有basic_info字段!")
    print(f"完整文档: {doc}")
