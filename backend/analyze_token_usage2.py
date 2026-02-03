#!/usr/bin/env python3
"""分析每次生成文案的token用量 - 找有数据的创作者"""

from database.connection import get_database

db = get_database()
profiles = db['user_profiles']
snapshots = db['user_snapshots']

# 找一个有笔记的创作者
print("🔍 查找有笔记数据的创作者...\n")
for profile in profiles.find({'platform': 'xiaohongshu'}):
    user_id = profile.get('user_id', '')
    if not user_id:
        continue
    
    notes_count = snapshots.count_documents({'user_id': user_id, 'platform': 'xiaohongshu'})
    if notes_count > 0:
        print(f'✅ 找到有数据的创作者: {profile.get("nickname", "N/A")}')
        print(f'   user_id: {user_id}')
        print(f'   笔记数: {notes_count}')
        
        # 获取5篇笔记
        notes = list(snapshots.find({'user_id': user_id, 'platform': 'xiaohongshu'}).limit(5))
        
        # 计算字符数
        topics_str = ", ".join(profile.get("topics", []))
        content_style = profile.get("content_style", "")
        value_points_str = "\n".join([f"- {vp}" for vp in profile.get("value_points", [])])
        
        profile_chars = len(topics_str) + len(content_style) + len(value_points_str)
        print(f'\n📊 档案信息: {profile_chars} 字符')
        print(f'   - 话题: {len(topics_str)} 字符')
        print(f'   - 风格: {len(content_style)} 字符')
        print(f'   - 价值观: {len(value_points_str)} 字符')
        
        # 笔记字符
        notes_chars = 0
        print(f'\n📝 笔记详情:')
        for i, note in enumerate(notes, 1):
            title = note.get('title', '')
            desc = note.get('desc', note.get('description', ''))
            note_len = len(title) + len(desc)
            notes_chars += note_len
            print(f'   笔记{i}: {note_len:,} 字符 (标题:{len(title)}, 内容:{len(desc):,})')
        
        print(f'\n📊 统计:')
        print(f'   档案信息: {profile_chars:,} 字符')
        print(f'   5篇笔记: {notes_chars:,} 字符')
        print(f'   总计: {profile_chars + notes_chars:,} 字符')
        
        # 估算token（中文 ≈ 1.8 tokens/字符）
        estimated_input_tokens = int((profile_chars + notes_chars) * 1.8)
        estimated_output_tokens = 1440  # 假设生成800字
        
        print(f'\n💰 Token估算:')
        print(f'   输入: ~{estimated_input_tokens:,} tokens')
        print(f'   输出: ~{estimated_output_tokens:,} tokens')
        print(f'   单次总计: ~{estimated_input_tokens + estimated_output_tokens:,} tokens')
        
        print(f'\n📈 成本分析 (基于DeepSeek价格):')
        # DeepSeek价格: 输入 $0.27/M tokens, 输出 $1.1/M tokens
        input_cost_per_100 = (estimated_input_tokens * 100 * 0.27) / 1_000_000
        output_cost_per_100 = (estimated_output_tokens * 100 * 1.1) / 1_000_000
        total_cost_per_100 = input_cost_per_100 + output_cost_per_100
        
        print(f'   生成100次:')
        print(f'     - 输入: ${input_cost_per_100:.4f}')
        print(f'     - 输出: ${output_cost_per_100:.4f}')
        print(f'     - 总计: ${total_cost_per_100:.4f}')
        
        break
