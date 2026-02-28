#!/usr/bin/env python3
"""
批量为所有笔记生成 embedding 向量

读取 user_snapshots 集合中的所有笔记，使用 BAAI/bge-small-zh-v1.5 模型
生成 512 维 embedding，存入 note_embeddings 集合。

用法：
    cd backend
    source ../.venv/bin/activate
    python scripts/generate_note_embeddings.py

参数：
    --batch-size    每批编码的笔记数（默认 64）
    --force         强制重新生成所有（覆盖已有）
"""

import sys
import time
import argparse
from pathlib import Path

# 确保能 import backend 包
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from database.connection import get_database
from core.config import settings


def load_embedding_model():
    """加载本地 FlagModel"""
    print(f"📦 加载 embedding 模型: {settings.EMBEDDING_MODEL}")
    t0 = time.time()
    from FlagEmbedding import FlagModel
    model = FlagModel(
        settings.EMBEDDING_MODEL,
        query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
        use_fp16=True
    )
    print(f"   ✅ 模型加载完成 ({time.time() - t0:.1f}s)")
    return model


def extract_notes_from_snapshots(db) -> list:
    """从 user_snapshots 提取所有笔记，并关联用户信息"""
    print("\n📋 从 user_snapshots 提取笔记...")

    snapshots = list(db.user_snapshots.find({}, {
        "user_id": 1, "notes": 1, "_id": 0
    }))
    print(f"   找到 {len(snapshots)} 个用户快照")

    # 预加载用户信息
    profiles = {}
    for p in db.user_profiles.find({}, {
        "user_id": 1, "nickname": 1, "basic_info": 1, "_id": 0
    }):
        uid = p.get("user_id", "")
        profiles[uid] = {
            "nickname": p.get("nickname", ""),
            "avatar": p.get("basic_info", {}).get("avatar", "") if isinstance(p.get("basic_info"), dict) else "",
        }

    all_notes = []
    for snap in snapshots:
        uid = snap.get("user_id", "")
        notes = snap.get("notes", [])
        user_info = profiles.get(uid, {"nickname": "", "avatar": ""})

        for note in notes:
            note_id = note.get("id") or note.get("note_id") or ""
            if not note_id:
                continue

            title = note.get("title", "")
            desc = note.get("desc", "")

            # 至少要有标题或描述
            if not title and not desc:
                continue

            likes = note.get("likes", 0) or 0
            collected = note.get("collected_count", 0) or 0
            comments = note.get("comments_count", 0) or 0
            shares = note.get("share_count", 0) or 0
            create_time = note.get("create_time", 0) or 0

            # 综合互动指数 = likes + collected*2 + comments*3 + shares*4
            engagement = likes + collected * 2 + comments * 3 + shares * 4

            all_notes.append({
                "note_id": note_id,
                "user_id": uid,
                "title": title,
                "desc": desc,
                "likes": likes,
                "collected_count": collected,
                "comments_count": comments,
                "share_count": shares,
                "engagement_score": float(engagement),
                "nickname": user_info["nickname"],
                "avatar": user_info["avatar"],
                "note_create_time": create_time,
                # 用于编码的文本
                "_embed_text": f"{title} {desc}".strip(),
            })

    print(f"   提取到 {len(all_notes)} 条有效笔记")
    return all_notes


def generate_embeddings(model, notes: list, batch_size: int = 64) -> list:
    """批量生成 embedding"""
    print(f"\n🔄 批量生成 embedding (batch_size={batch_size})...")

    texts = [n["_embed_text"] for n in notes]
    all_embeddings = []

    total_batches = (len(texts) + batch_size - 1) // batch_size
    t0 = time.time()

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        batch_num = i // batch_size + 1

        vecs = model.encode(batch_texts)  # numpy array (batch, dim)
        if hasattr(vecs, "tolist"):
            vecs_list = vecs.tolist()
        else:
            vecs_list = np.array(vecs).tolist()

        all_embeddings.extend(vecs_list)

        elapsed = time.time() - t0
        rate = (i + len(batch_texts)) / elapsed if elapsed > 0 else 0
        print(f"   [{batch_num}/{total_batches}] "
              f"已编码 {i + len(batch_texts)}/{len(texts)} "
              f"({rate:.1f} notes/s)")

    print(f"   ✅ 编码完成，总耗时 {time.time() - t0:.1f}s")
    return all_embeddings


def save_to_mongodb(db, notes: list, embeddings: list, force: bool = False):
    """写入 note_embeddings 集合"""
    print(f"\n💾 写入 MongoDB note_embeddings 集合...")

    collection = db.note_embeddings

    # 如果不 force，先检查已存在的
    existing_ids = set()
    if not force:
        existing = collection.find({}, {"note_id": 1, "_id": 0})
        existing_ids = {doc["note_id"] for doc in existing}
        print(f"   已存在 {len(existing_ids)} 条，跳过")

    from pymongo import UpdateOne
    operations = []
    skipped = 0

    for note, emb in zip(notes, embeddings):
        if not force and note["note_id"] in existing_ids:
            skipped += 1
            continue

        doc = {
            "note_id": note["note_id"],
            "user_id": note["user_id"],
            "platform": "xiaohongshu",
            "title": note["title"],
            "desc": note["desc"],
            "embedding": emb,
            "model": settings.EMBEDDING_MODEL,
            "dimension": settings.EMBEDDING_DIMENSION,
            "likes": note["likes"],
            "collected_count": note["collected_count"],
            "comments_count": note["comments_count"],
            "share_count": note["share_count"],
            "engagement_score": note["engagement_score"],
            "nickname": note["nickname"],
            "avatar": note["avatar"],
            "note_create_time": note["note_create_time"],
        }

        operations.append(UpdateOne(
            {"note_id": note["note_id"]},
            {"$set": doc, "$setOnInsert": {"created_at": __import__("datetime").datetime.now()}},
            upsert=True
        ))

    if operations:
        # 分批写入
        batch = 500
        total_upserted = 0
        total_modified = 0
        for i in range(0, len(operations), batch):
            result = collection.bulk_write(operations[i:i + batch])
            total_upserted += result.upserted_count
            total_modified += result.modified_count
            print(f"   批次 {i // batch + 1}: "
                  f"新增 {result.upserted_count}, 更新 {result.modified_count}")

        print(f"\n   ✅ 写入完成: 新增 {total_upserted}, 更新 {total_modified}, 跳过 {skipped}")
    else:
        print(f"   ℹ️  没有需要写入的数据 (跳过 {skipped})")


def create_note_indexes(db):
    """创建必要的索引"""
    print("\n📊 创建索引...")
    collection = db.note_embeddings

    indexes = [
        ("note_id_unique", [("note_id", 1)], {"unique": True}),
        ("user_id", [("user_id", 1)], {}),
        ("engagement_score_desc", [("engagement_score", -1)], {}),
        ("note_create_time_desc", [("note_create_time", -1)], {}),
    ]

    for name, keys, opts in indexes:
        try:
            collection.create_index(keys, name=name, **opts)
            print(f"   ✅ {name}")
        except Exception as e:
            if "already exists" in str(e):
                print(f"   ℹ️  {name} (已存在)")
            else:
                print(f"   ❌ {name}: {e}")


def main():
    parser = argparse.ArgumentParser(description="为笔记生成 embedding 向量")
    parser.add_argument("--batch-size", type=int, default=64, help="每批编码数量")
    parser.add_argument("--force", action="store_true", help="强制覆盖已有 embedding")
    args = parser.parse_args()

    print("=" * 60)
    print("🚀 笔记 Embedding 批量生成工具")
    print("=" * 60)
    print(f"  模型: {settings.EMBEDDING_MODEL}")
    print(f"  维度: {settings.EMBEDDING_DIMENSION}")
    print(f"  批大小: {args.batch_size}")
    print(f"  强制覆盖: {args.force}")

    t_total = time.time()

    # 1. 连接数据库
    db = get_database()

    # 2. 提取笔记
    notes = extract_notes_from_snapshots(db)
    if not notes:
        print("\n⚠️  没有找到任何笔记，请先运行数据采集")
        return

    # 3. 加载模型
    model = load_embedding_model()

    # 4. 生成 embedding
    embeddings = generate_embeddings(model, notes, batch_size=args.batch_size)

    # 5. 写入 MongoDB
    save_to_mongodb(db, notes, embeddings, force=args.force)

    # 6. 创建索引
    create_note_indexes(db)

    # 7. 统计
    final_count = db.note_embeddings.count_documents({})
    print(f"\n{'=' * 60}")
    print(f"✅ 全部完成！")
    print(f"  note_embeddings 集合: {final_count} 条")
    print(f"  总耗时: {time.time() - t_total:.1f}s")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
