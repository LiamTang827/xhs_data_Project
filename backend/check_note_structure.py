#!/usr/bin/env python3
"""
检查笔记数据结构，看看有哪些字段
"""

import sys
from pathlib import Path
import json

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from database import UserSnapshotRepository

def check_note_structure(user_id: str):
    """检查笔记结构"""
    print(f"检查用户: {user_id}")
    
    # 获取snapshot
    snapshot_repo = UserSnapshotRepository()
    snapshot = snapshot_repo.get_by_user_id(user_id, "xiaohongshu")
    
    if not snapshot:
        print("❌ 未找到笔记数据")
        return
    
    notes = snapshot.get('notes', [])
    print(f"✅ 找到 {len(notes)} 条笔记")
    
    if notes:
        print("\n第一条笔记的所有字段:")
        first_note = notes[0]
        for key in sorted(first_note.keys()):
            value = first_note[key]
            if isinstance(value, str):
                value_str = value[:50] if len(value) > 50 else value
            elif isinstance(value, list):
                value_str = f"[{len(value)} items]"
            elif isinstance(value, dict):
                value_str = f"{{...}}"
            else:
                value_str = str(value)
            print(f"  {key}: {value_str}")
        
        # 检查是否有tag相关字段
        print("\n🔍 查找tag相关字段:")
        tag_fields = [k for k in first_note.keys() if 'tag' in k.lower()]
        if tag_fields:
            print(f"✅ 发现tag字段: {tag_fields}")
            for field in tag_fields:
                print(f"\n{field} 示例:")
                print(json.dumps(first_note[field], indent=2, ensure_ascii=False))
        else:
            print("❌ 没有找到tag相关字段")
        
        # 检查前3条笔记的tag
        print("\n📝 前3条笔记的可能tag来源:")
        for i, note in enumerate(notes[:3], 1):
            print(f"\n笔记 {i}: {note.get('title', '')[:30]}")
            
            # 检查各种可能的tag字段
            for field in ['tag_list', 'tags', 'topic_list', 'topics', 'hashtags']:
                if field in note:
                    print(f"  ✅ {field}: {note[field]}")

if __name__ == "__main__":
    # 测试一个已存在的用户
    check_note_structure("5e6472940000000001008d4e")  # 图灵星球
