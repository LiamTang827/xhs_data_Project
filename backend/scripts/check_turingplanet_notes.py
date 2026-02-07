"""检查图灵星球的笔记内容"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.connection import get_database
from datetime import datetime, timedelta
import re

db = get_database()
snapshots = db['user_snapshots']
profiles = db['user_profiles']

# 查找图灵星球的profile
print("查找图灵星球的profile...")
profile = None
all_profiles = list(profiles.find({}, {'user_id': 1, 'basic_info.nickname': 1}))
for p in all_profiles:
    nick = p.get('basic_info', {}).get('nickname', '')
    if '图灵' in nick:
        profile = p
        user_id = p.get('user_id')
        print(f"✅ 找到: {nick} - {user_id}")
        break

if not profile:
    print('❌ 未找到图灵星球')
    exit(1)

# 查找snapshot
print("\n查找snapshot...")
snapshot = snapshots.find_one({'user_id': user_id})
if snapshot:
    notes = snapshot.get('notes', [])
    print(f'✅ 找到snapshot: {len(notes)} 篇笔记')
    
    # 最近30天
    cutoff_time = datetime.now() - timedelta(days=30)
    cutoff_ts = int(cutoff_time.timestamp())
    recent_notes = [n for n in notes if n.get('create_time', 0) >= cutoff_ts]
    
    print(f'最近30天: {len(recent_notes)} 篇笔记\n')
    
    for i, note in enumerate(recent_notes, 1):
        title = note.get('title', '') or ''
        desc = note.get('desc', '') or ''
        print('='*60)
        print(f'笔记 {i}:')
        print(f'  标题: {title}')
        print(f'  描述: {desc[:200]}...' if len(desc) > 200 else f'  描述: {desc}')
        
        text = title + ' ' + desc
        tags = re.findall(r'#([\w\u4e00-\u9fa5]+)', text)
        print(f'  提取到的#标签: {tags}')
else:
    print('❌ 未找到snapshot')

