"""
批量刷新用户数据 - 只刷新最近30天没笔记的账号
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
collectors_path = project_root.parent / 'collectors' / 'xiaohongshu'
sys.path.insert(0, str(collectors_path))

from database.connection import get_database
from collector import fetch_user_notes, fetch_user_info, save_to_mongodb


def refresh_all_users():
    """只刷新最近30天0笔记的账号"""
    print("=" * 60)
    print("🔄 刷新最近30天无笔记的账号")
    print("=" * 60)
    
    db = get_database()
    snapshots = db['user_snapshots']
    profiles = db['user_profiles']
    
    # 获取所有用户
    all_profiles = list(profiles.find({}, {'user_id': 1, 'basic_info.nickname': 1}))
    
    # 计算30天前的时间戳
    cutoff_time = datetime.now() - timedelta(days=30)
    cutoff_ts = int(cutoff_time.timestamp())
    
    # 找出最近30天0笔记的账号
    to_refresh = []
    for p in all_profiles:
        user_id = p.get('user_id')
        nickname = p.get('basic_info', {}).get('nickname', 'Unknown')
        
        snapshot = snapshots.find_one({'user_id': user_id})
        if snapshot:
            notes = snapshot.get('notes', [])
            recent_notes = [n for n in notes if n.get('create_time', 0) >= cutoff_ts]
            if len(recent_notes) == 0:
                to_refresh.append((user_id, nickname))
        else:
            to_refresh.append((user_id, nickname))
    
    total = len(to_refresh)
    print(f"\n✅ 需要刷新 {total} 个账号\n")
    
    success = 0
    fail = 0
    
    for i, (user_id, nickname) in enumerate(to_refresh, 1):
        print(f"[{i}/{total}] 🔄 {nickname} ({user_id[:12]}...)")
        
        try:
            # 获取最新数据
            notes_result = fetch_user_notes(user_id)
            notes = notes_result.get('notes', [])
            
            user_info = fetch_user_info(user_id)
            fans = user_info.get('fans', 0)
            
            # 保存
            save_to_mongodb(user_id, {'notes': notes, 'user_info': user_info})
            
            print(f"  ✅ {len(notes)}篇笔记, {fans:,}粉丝")
            success += 1
            
        except Exception as e:
            print(f"  ❌ {str(e)}")
            fail += 1
    
    print("\n" + "=" * 60)
    print(f"✅ 成功: {success}/{total}")
    print(f"❌ 失败: {fail}/{total}")
    print("=" * 60)


if __name__ == "__main__":
    refresh_all_users()
