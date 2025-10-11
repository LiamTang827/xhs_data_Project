"""
测试脚本：验证 content_snapshot 数据格式

这个脚本会帮助你：
1. 理解新的 content_snapshot 数据格式
2. 调试为什么之前的 interact_info 是 0
"""

import datetime

# 模拟小红书 API 返回的原始数据（可能的格式）
mock_api_response = {
    "data": {
        "items": [{
            "id": "6789abcdef123456",
            "note_card": {
                "type": "normal",  # 或 "video"
                "title": "这是一篇测试笔记",
                "desc": "这是笔记的详细描述内容...",
                "time": 1697123456000,  # 毫秒时间戳
                "user": {
                    "user_id": "user_123",
                    "id": "user_123",
                    "nickname": "测试用户"
                },
                "interact_info": {
                    # 🔴 关键发现：这些值可能是字符串！
                    "liked_count": "2.7万",  # ← 这就是为什么是0的原因！
                    "collected_count": "1234",
                    "comment_count": "567",
                    "share_count": "89"
                },
                "tag_list": [
                    {"name": "旅游"},
                    {"name": "美食"}
                ]
            }
        }]
    }
}

# 模拟评论数据
mock_comments = [
    {
        "user_info": {
            "user_id": "commenter_1",
            "nickname": "评论者A"
        },
        "content": "这是一条评论",
        "create_time": 1697123456,
        "like_count": "123"  # 也可能是字符串
    },
    {
        "user_info": {
            "user_id": "commenter_2",
            "nickname": "评论者B"
        },
        "content": "另一条评论",
        "create_time": 1697123457,
        "like_count": 45  # 或整数
    }
]

def safe_int(value, default=0):
    """安全转换为整数（支持中文数字）"""
    if value is None:
        return default
    
    try:
        if isinstance(value, int):
            return value
        
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return default
            
            # 处理"万"
            if '万' in value:
                num_str = value.replace('万', '').strip()
                return int(float(num_str) * 10000)
            
            # 处理"千"
            if '千' in value:
                num_str = value.replace('千', '').strip()
                return int(float(num_str) * 1000)
            
            # 普通数字字符串
            return int(float(value))
        
        return int(value)
        
    except (ValueError, TypeError):
        return default

# 解析数据
note_data = mock_api_response['data']['items'][0]
note_card = note_data['note_card']

print("=" * 60)
print("🔍 调试：为什么 interact_info 是 0？")
print("=" * 60)

# 提取互动数据
interact_info = note_card['interact_info']
print(f"\n原始数据类型检查：")
print(f"  liked_count 原始值: {interact_info['liked_count']!r}")
print(f"  liked_count 类型: {type(interact_info['liked_count'])}")

print(f"\n❌ 错误的做法（直接 get，导致返回字符串）：")
wrong_liked = interact_info.get('liked_count', 0)
print(f"  结果: {wrong_liked!r} (类型: {type(wrong_liked)})")
print(f"  问题: 这是字符串 '2.7万'，不是数字！")

print(f"\n✅ 正确的做法（使用 safe_int 转换）：")
correct_liked = safe_int(interact_info.get('liked_count', 0))
print(f"  结果: {correct_liked} (类型: {type(correct_liked)})")
print(f"  成功: '2.7万' → 27000")

print("\n" + "=" * 60)
print("📊 新的 content_snapshot 格式")
print("=" * 60)

# 构建 content_snapshot
user = note_card['user']
published_time = datetime.datetime.fromtimestamp(
    note_card['time'] / 1000, 
    tz=datetime.timezone.utc
)

formatted_comments = []
for comment in mock_comments:
    formatted_comment = {
        "commenter_id": comment['user_info']['user_id'],
        "commenter_name": comment['user_info']['nickname'],
        "comment_content": comment['content'],
        "published_time": comment['create_time'],
        "likes_on_comment": safe_int(comment.get('like_count', 0))
    }
    formatted_comments.append(formatted_comment)

content_snapshot = {
    "channel_id": user['user_id'],
    "content_id": note_data['id'],
    "content_type": "video" if note_card['type'] == 'video' else "note",
    "content_title": note_card['title'],
    "likes": safe_int(interact_info.get('liked_count', 0)),
    "shares": safe_int(interact_info.get('share_count', 0)),
    "views": 0,
    "published_time": published_time,
    "collected_number": safe_int(interact_info.get('collected_count', 0)),
    "comments": formatted_comments,
    "description": note_card['desc'],
    "tags": [tag['name'] for tag in note_card['tag_list']],
}

print("\n📋 完整的 content_snapshot 结构：\n")
import json
print(json.dumps(content_snapshot, indent=2, ensure_ascii=False, default=str))

print("\n" + "=" * 60)
print("✅ 关键改进点")
print("=" * 60)
print("""
1. ✅ 使用 safe_int() 转换所有数字字段
   - liked_count: '2.7万' → 27000
   - collected_count: '1234' → 1234
   
2. ✅ 新的字段映射：
   - note_id → content_id
   - liked_count → likes
   - collected_count → collected_number
   - user_id → channel_id
   
3. ✅ 评论格式化：
   - 扁平化评论数据
   - 标准化字段名
   
4. ✅ 添加日志输出：
   - 每次保存都会记录实际数值
   - 方便调试
""")

print("\n" + "=" * 60)
print("🧪 测试建议")
print("=" * 60)
print("""
1. 重启 FastAPI 服务器
2. 调用 /note/info?note_url=你的笔记URL
3. 检查日志输出：
   - 看到 "likes=27000" 说明转换成功
   - 看到 "likes=0" 说明 API 数据结构可能不同
4. 查看 MongoDB 数据库中的 notes 集合
5. 如果还是 0，把完整的 API 响应日志发给我
""")
