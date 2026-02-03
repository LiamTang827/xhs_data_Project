#!/usr/bin/env python3
"""分析每次生成文案的token用量"""

from database.connection import get_database

db = get_database()
profiles = db['user_profiles']
snapshots = db['user_snapshots']

# 获取一个创作者的资料
profile = profiles.find_one({'platform': 'xiaohongshu'})
if profile:
    print(f'创作者昵称: {profile.get("nickname", "N/A")}')
    print(f'话题数量: {len(profile.get("topics", []))}')
    print(f'价值观数量: {len(profile.get("value_points", []))}')
    
    # 获取5篇笔记
    user_id = profile.get('user_id', '')
    notes = list(snapshots.find({'user_id': user_id, 'platform': 'xiaohongshu'}).limit(5))
    print(f'笔记数量: {len(notes)}')
    
    # 计算总字符数
    total_chars = 0
    
    # 档案字符
    topics_str = ", ".join(profile.get("topics", []))
    content_style = profile.get("content_style", "")
    value_points_str = "\n".join([f"- {vp}" for vp in profile.get("value_points", [])])
    
    profile_chars = len(topics_str) + len(content_style) + len(value_points_str)
    print(f'\n📊 档案信息约: {profile_chars} 字符')
    
    # 笔记字符
    notes_chars = 0
    for i, note in enumerate(notes, 1):
        title = note.get('title', '')
        desc = note.get('desc', note.get('description', ''))
        note_len = len(title) + len(desc)
        notes_chars += note_len
        print(f'  笔记{i}: {note_len} 字符 (标题:{len(title)}, 内容:{len(desc)})')
    
    print(f'\n📊 5篇笔记总计: {notes_chars} 字符')
    print(f'📊 档案+笔记总计: {profile_chars + notes_chars} 字符')
    
    # 估算token（中文字符 ≈ 1.5-2 tokens，这里取1.8）
    estimated_input_tokens = int((profile_chars + notes_chars) * 1.8)
    print(f'\n💰 估算输入token: {estimated_input_tokens:,} tokens')
    print(f'💰 估算输出token (假设生成800字): ~1,440 tokens')
    print(f'💰 单次生成总计: ~{estimated_input_tokens + 1440:,} tokens')
    
    print(f'\n📈 如果生成100次:')
    print(f'   - 输入: {estimated_input_tokens * 100:,} tokens')
    print(f'   - 输出: 144,000 tokens')
    print(f'   - 总计: ~{(estimated_input_tokens + 1440) * 100:,} tokens')
