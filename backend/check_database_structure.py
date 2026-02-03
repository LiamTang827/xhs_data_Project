#!/usr/bin/env python3
"""检查数据库结构和数据完整性"""

from database.connection import get_database

db = get_database()

print("=" * 60)
print("📊 数据库结构分析")
print("=" * 60)

# 1. 检查 user_profiles
print("\n1️⃣ user_profiles 集合：")
profiles = list(db.user_profiles.find({'platform': 'xiaohongshu'}).limit(5))
print(f"   总数: {db.user_profiles.count_documents({'platform': 'xiaohongshu'})}")

if profiles:
    sample = profiles[0]
    print(f"\n   样本字段:")
    for key in sample.keys():
        value = sample[key]
        if isinstance(value, dict):
            print(f"   - {key}: {{...}} (嵌套对象)")
            for sub_key in list(value.keys())[:5]:
                print(f"     - {sub_key}: {type(value[sub_key]).__name__}")
        elif isinstance(value, list):
            print(f"   - {key}: [...] (列表，长度: {len(value)})")
        else:
            print(f"   - {key}: {type(value).__name__}")
    
    print(f"\n   所有创作者的字段检查:")
    for profile in profiles:
        nickname = profile.get('nickname', 'N/A')
        has_fans = 'fans' in profile or ('profile_data' in profile and 'fans' in profile.get('profile_data', {}))
        has_topics = 'topics' in profile or ('profile_data' in profile and 'topics' in profile.get('profile_data', {}))
        print(f"   - {nickname}: fans={has_fans}, topics={has_topics}")

# 2. 检查 user_snapshots
print("\n2️⃣ user_snapshots 集合：")
snapshot = db.user_snapshots.find_one({'platform': 'xiaohongshu'})
if snapshot:
    print(f"   总数: {db.user_snapshots.count_documents({'platform': 'xiaohongshu'})}")
    print(f"   样本字段:")
    for key in snapshot.keys():
        if key == 'notes':
            print(f"   - notes: 笔记数 = {len(snapshot[key])}")
            if snapshot[key]:
                note = snapshot[key][0]
                print(f"     笔记字段: {list(note.keys())}")
        else:
            print(f"   - {key}: {type(snapshot[key]).__name__}")

# 3. 提取所有话题词（用于流量密码）
print("\n3️⃣ 话题词汇分析（流量密码候选）：")
all_topics = []
for profile in db.user_profiles.find({'platform': 'xiaohongshu'}):
    # 尝试不同的字段位置
    topics = []
    if 'topics' in profile:
        topics = profile['topics']
    elif 'profile_data' in profile and 'topics' in profile['profile_data']:
        topics = profile['profile_data']['topics']
    elif 'profile_data' in profile and 'content_topics' in profile['profile_data']:
        topics = profile['profile_data']['content_topics']
    
    all_topics.extend(topics)

from collections import Counter
topic_counter = Counter(all_topics)
print(f"   总话题数: {len(all_topics)}")
print(f"   唯一话题数: {len(topic_counter)}")
print(f"\n   🔥 Top 20 热门话题（流量密码）:")
for topic, count in topic_counter.most_common(20):
    print(f"   - {topic}: {count}次")

# 4. 检查creator_networks
print("\n4️⃣ creator_networks 集合：")
network_count = db.creator_networks.count_documents({'platform': 'xiaohongshu'})
print(f"   总数: {network_count}")
if network_count > 0:
    network = db.creator_networks.find_one({'platform': 'xiaohongshu'})
    if network and 'network_data' in network:
        data = network['network_data']
        print(f"   创作者数: {len(data.get('creators', []))}")
        print(f"   边数: {len(data.get('creatorEdges', []))}")

print("\n" + "=" * 60)
