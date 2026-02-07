#!/usr/bin/env python3
"""
从数据库中已有的profiles和snapshots初始化creator_networks
如果网络中的创作者少于数据库中的profiles，就重新生成
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import UserProfileRepository, UserSnapshotRepository, CreatorNetworkRepository


def check_and_init_network():
    """检查并初始化网络"""
    print("=" * 60)
    print("🔍 检查创作者网络数据完整性")
    print("=" * 60)
    
    profile_repo = UserProfileRepository()
    snapshot_repo = UserSnapshotRepository()
    network_repo = CreatorNetworkRepository()
    
    # 1. 统计数据库中的数据
    print("\n📊 数据库统计:")
    profiles = list(profile_repo.collection.find({'platform': 'xiaohongshu'}))
    snapshots = list(snapshot_repo.collection.find({'platform': 'xiaohongshu'}))
    
    print(f"  • user_profiles: {len(profiles)} 个")
    print(f"  • user_snapshots: {len(snapshots)} 个")
    
    # 显示所有创作者
    print("\n📋 数据库中的创作者:")
    for p in profiles:
        basic_info = p.get('basic_info', {})
        stats = p.get('stats', {})
        nickname = basic_info.get('nickname', 'Unknown')
        fans = stats.get('fans', 0)
        user_id = p.get('user_id', 'Unknown')
        print(f"  • {nickname:30} - 粉丝: {fans:>10,} - ID: {user_id[:16]}...")
    
    # 2. 检查网络数据
    network = network_repo.collection.find_one({'platform': 'xiaohongshu'})
    
    if network:
        network_data = network.get('network_data', {})
        creators = network_data.get('creators', [])
        print(f"\n🌐 creator_networks: {len(creators)} 个创作者")
        
        # 检查是否匹配
        if len(creators) >= len(profiles):
            print("\n✅ 网络数据完整，无需重新生成")
            return
    else:
        print(f"\n🌐 creator_networks: 未找到网络数据")
    
    # 3. 需要重新生成
    print("\n⚠️  网络数据不完整或缺失，需要重新生成")
    
    # 检查是否有snapshot数据
    if len(snapshots) < len(profiles):
        print(f"\n⚠️  警告: snapshots ({len(snapshots)}) 少于 profiles ({len(profiles)})")
        print("   某些创作者可能没有笔记数据，将被跳过")
    
    # 4. 执行重新生成
    print("\n" + "=" * 60)
    print("🔄 开始重新生成创作者网络...")
    print("=" * 60)
    
    import subprocess
    import os
    
    backend_dir = Path(__file__).parent.parent
    script_path = backend_dir / "scripts" / "regenerate_creator_networks.py"
    
    result = subprocess.run(
        ["python3", str(script_path)],
        cwd=str(backend_dir),
        capture_output=False
    )
    
    if result.returncode == 0:
        print("\n✅ 网络重新生成成功！")
    else:
        print(f"\n❌ 网络重新生成失败，退出码: {result.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        check_and_init_network()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
