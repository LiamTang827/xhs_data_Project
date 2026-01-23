#!/usr/bin/env python3
"""
Generate creators_data.json from snapshots for FastAPI
从snapshots目录生成创作者网络数据，输出为JSON格式供FastAPI使用
使用analyses目录中的embedding数据计算创作者之间的余弦相似度
"""
import json
import re
import math
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent.parent  # data-analysiter根目录
DATA_DIR = BASE / 'data'
SNAP_DIR = DATA_DIR / 'snapshots'
ANALYSES_DIR = DATA_DIR / 'analyses'
OUT_JSON = DATA_DIR / 'creators_data.json'

WEIGHT_FOLLOWERS = 0.6
WEIGHT_INTERACTION = 0.4
SIMILARITY_THRESHOLD = 0.7  # 余弦相似度阈值，高于此值才建立边

def safe_int(v):
    try:
        return int(v)
    except Exception:
        try:
            return int(float(v))
        except Exception:
            return 0

def load_json(p: Path):
    return json.loads(p.read_text(encoding='utf-8'))

def parse_date_from_filename(fn: str):
    """从文件名中解析日期，例如：大圆镜科普_2025-11-17.json"""
    m = re.match(r'.+?_(\d{4}-\d{2}-\d{2})', fn)
    if m:
        try:
            return datetime.fromisoformat(m.group(1))
        except Exception:
            return None
    return None

def calculate_influence(followers, interaction):
    """计算影响力指数"""
    return round(WEIGHT_FOLLOWERS * followers + WEIGHT_INTERACTION * interaction)

def cosine_similarity(vec1, vec2):
    """计算两个向量的余弦相似度"""
    if len(vec1) != len(vec2):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)

def load_embedding(creator_name):
    """加载创作者的embedding向量"""
    # 尝试多种文件名格式
    possible_names = [
        f"{creator_name}__embedding.json",
        f"{creator_name}_embedding.json",
    ]
    
    for name in possible_names:
        path = ANALYSES_DIR / name
        if path.exists():
            try:
                data = load_json(path)
                # 兼容 analyze.py 的新输出格式 (user_style_embedding) 和旧格式 (embedding)
                return data.get('user_style_embedding') or data.get('embedding', [])
            except Exception as e:
                print(f'⚠️  读取embedding失败 {name}: {e}')
    
    return None

def main():
    if not SNAP_DIR.exists():
        print(f'❌ 快照目录不存在: {SNAP_DIR}')
        return

    files = [p for p in SNAP_DIR.iterdir() if p.is_file() and p.name.endswith('.json')]
    if not files:
        print(f'❌ 快照目录中没有JSON文件: {SNAP_DIR}')
        return

    # 按创作者名称分组
    groups = {}
    for p in files:
        # 从文件名提取创作者名称（去掉日期后缀）
        base_name = p.stem
        creator_name = re.sub(r'_\d{4}-\d{2}-\d{2}$', '', base_name)
        
        if creator_name not in groups:
            groups[creator_name] = []
        groups[creator_name].append(p)

    print(f'📊 找到 {len(groups)} 个创作者，共 {len(files)} 个快照文件')

    creators = []
    
    for creator_name, paths in groups.items():
        # 按日期排序
        sorted_paths = sorted(paths, key=lambda x: parse_date_from_filename(x.name) or datetime.min)
        
        if not sorted_paths:
            continue
        
        # 读取所有快照
        snapshots = []
        for path in sorted_paths:
            try:
                data = load_json(path)
                date = parse_date_from_filename(path.name)
                # 支持两种格式：user_basic (user_profiles) 和 user (snapshots)
                if date and ('user_basic' in data or 'user' in data):
                    snapshots.append({
                        'date': date,
                        'data': data
                    })
            except Exception as e:
                print(f'⚠️  读取快照失败 {path.name}: {e}')
        
        if not snapshots:
            continue
        
        # 使用最新快照作为当前数据
        latest_snapshot = snapshots[-1]
        latest_data = latest_snapshot['data']
        
        # 兼容两种格式
        user_basic = latest_data.get('user_basic') or latest_data.get('user', {})
        
        user_id = user_basic.get('user_id', '')
        nickname = user_basic.get('nickname', creator_name)
        followers = safe_int(user_basic.get('fans', 0))
        interaction = safe_int(user_basic.get('interaction', 0))
        
        # 构建时间序列数据
        # 前端需要两种格式：
        # 1. indexSeriesRaw - 详细数据用于悬停提示
        # 2. indexSeries - 简化数据 [{ts, value}] 用于图表绘制
        index_series_raw = []
        index_series = []
        
        for snap in snapshots:
            snap_user = snap['data'].get('user_basic') or snap['data'].get('user', {})
            snap_followers = safe_int(snap_user.get('fans', 0))
            snap_interaction = safe_int(snap_user.get('interaction', 0))
            snap_influence = calculate_influence(snap_followers, snap_interaction)
            snap_ts = int(snap['date'].timestamp() * 1000)
            
            # 详细数据
            index_series_raw.append({
                'time': snap['date'].isoformat(),
                'followers': snap_followers,
                'interaction': snap_interaction,
                'influence': snap_influence,
                'ts': snap_ts,
                'value': snap_influence
            })
            
            # 简化数据（前端图表用）
            index_series.append({
                'ts': snap_ts,
                'value': snap_influence
            })
        
        # 计算增长Delta（如果有多个快照）
        followers_delta = 0
        interaction_delta = 0
        if len(snapshots) >= 2:
            prev_snapshot = snapshots[-2]
            prev_user = prev_snapshot['data'].get('user_basic') or prev_snapshot['data'].get('user', {})
            prev_followers = safe_int(prev_user.get('fans', 0))
            prev_interaction = safe_int(prev_user.get('interaction', 0))
            
            followers_delta = followers - prev_followers
            interaction_delta = interaction - prev_interaction
        
        # 构建创作者节点数据
        # 从user_profiles获取更多信息（如果存在）
        profile_path = DATA_DIR / 'user_profiles' / f'{nickname}.json'
        content_topics = []
        content_form = ''
        if profile_path.exists():
            try:
                profile_data = load_json(profile_path)
                content_topics = profile_data.get('content_topics', [])
                content_form = profile_data.get('content_style', {}).get('表达方式', '')
            except:
                pass
        
        creator_node = {
            'id': user_id,
            'name': nickname,
            'followers': followers,
            # 互动率 = 互动数 / 粉丝数 * 100，保留2位小数
            'engagementIndex': round((interaction / followers * 100), 2) if followers > 0 else 0,
            'primaryTrack': content_topics[0] if content_topics else '其他',
            'contentForm': content_form,
            'recentKeywords': content_topics[:5],
            'position': {'x': 0, 'y': 0},  # 前端会重新计算布局
            'avatar': user_basic.get('avatar', ''),
            'ipLocation': user_basic.get('ip_location', ''),
            'desc': user_basic.get('desc', ''),
            'followersDelta': followers_delta,
            'interactionDelta': interaction_delta,
            'indexSeriesRaw': index_series_raw,  # 详细数据
            'indexSeries': index_series  # 简化数据 [{ts, value}] 供图表使用
        }
        
        creators.append(creator_node)

    # 加载所有创作者的embedding向量
    print(f'\n📊 加载embedding向量...')
    print(f'创作者数量: {len(creators)}')
    embeddings = {}
    for creator in creators:
        name = creator['name']
        print(f'   尝试加载: {name} (ID: {creator["id"]})')
        embedding = load_embedding(name)
        if embedding:
            embeddings[creator['id']] = embedding
            print(f'   ✓ {name}: {len(embedding)} 维')
        else:
            print(f'   ✗ {name}: 未找到embedding')
    
    # 使用余弦相似度生成边数据
    print(f'\n🔗 计算创作者之间的余弦相似度...')
    edges = []
    for i, creator1 in enumerate(creators):
        for j, creator2 in enumerate(creators):
            if i >= j:
                continue
            
            id1 = creator1['id']
            id2 = creator2['id']
            
            # 如果两个创作者都有embedding，计算余弦相似度
            if id1 in embeddings and id2 in embeddings:
                similarity = cosine_similarity(embeddings[id1], embeddings[id2])
                
                # 只保留相似度高于阈值的边
                if similarity >= SIMILARITY_THRESHOLD:
                    edges.append({
                        'source': id1,
                        'target': id2,
                        'weight': round(similarity, 3),
                        'types': {
                            'style': round(similarity, 3)  # 使用style类型表示内容风格相似度
                        }
                    })
                    print(f'   {creator1["name"]} ↔ {creator2["name"]}: {similarity:.3f}')
    
    print(f'\n✅ 生成了 {len(edges)} 条边（相似度阈值 ≥ {SIMILARITY_THRESHOLD}）')

    # 按主题聚类
    track_clusters = {}
    for creator in creators:
        track = creator.get('primaryTrack', '其他')
        if track not in track_clusters:
            track_clusters[track] = []
        track_clusters[track].append(creator['id'])

    # 输出数据
    output_data = {
        'creators': creators,
        'creatorEdges': edges,
        'trackClusters': track_clusters,
        'trendingKeywordGroups': []  # 可以后续扩展
    }

    OUT_JSON.write_text(
        json.dumps(output_data, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )

    print(f'✅ 已生成创作者数据: {OUT_JSON}')
    print(f'   - {len(creators)} 个创作者')
    print(f'   - {len(edges)} 条关系边')
    print(f'   - {len(track_clusters)} 个主题聚类')

if __name__ == '__main__':
    main()
