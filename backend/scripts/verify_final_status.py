#!/usr/bin/env python3
"""验证最终的embedding统一状态"""

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root / "backend"))

from database.connection import get_database

db = get_database()

print('\n' + '='*70)
print('所有用户embedding详情:')
print('='*70)

embeddings = list(db.user_embeddings.find({'platform': 'xiaohongshu'}))
for i, e in enumerate(embeddings, 1):
    uid = e.get('user_id')
    dim = e.get('dimension')
    model = e.get('model')
    profile = db.user_profiles.find_one({'user_id': uid})
    nickname = profile.get('nickname', uid[:16]) if profile else uid[:16]
    print(f'{i:2d}. {nickname[:25]:25s} {dim}维  {model}')

# 统计
dims = {}
models = {}
for e in embeddings:
    d = e.get('dimension')
    m = e.get('model')
    dims[d] = dims.get(d, 0) + 1
    models[m] = models.get(m, 0) + 1

print('\n' + '='*70)
print('汇总统计:')
print('='*70)
print(f'总用户数: {len(embeddings)}')
print('\n维度分布:')
for d in sorted(dims):
    print(f'  {d}维: {dims[d]}个')
print('\n模型分布:')
for m, c in sorted(models.items()):
    print(f'  {m}: {c}个')

# 检查是否都是512维
if len(dims) == 1 and 512 in dims:
    print('\n✅ 太好了！所有embedding已统一为512维！')
    print('✅ 可以测试刷新网络功能了')
else:
    print(f'\n⚠️  还有问题，存在{len(dims)}种维度')
    for d, c in dims.items():
        if d != 512:
            print(f'  - {d}维: {c}个 (需要处理)')
