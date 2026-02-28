"""
笔记语义搜索服务
使用 BAAI/bge-small-zh-v1.5 embedding + numpy cosine similarity
"""

import time
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from database import NoteEmbeddingRepository


# =====================================================
# 内存缓存：笔记embedding矩阵
# =====================================================
_embedding_cache: Dict[str, Any] = {
    "note_ids": [],        # List[str] - 与矩阵行一一对应
    "matrix": None,        # numpy ndarray (N, 512)
    "metadata": {},        # Dict[note_id -> {title, desc, ...}]
    "loaded_at": None,     # datetime
    "ttl_seconds": 600,    # 缓存10分钟
}

# 全局 embedding model 实例（懒加载）
_embedding_model = None


def _get_embedding_model():
    """懒加载 FlagModel（首次调用时加载，约2-3秒）"""
    global _embedding_model
    if _embedding_model is None:
        print("[NoteSearch] 加载 embedding 模型 BAAI/bge-small-zh-v1.5 ...")
        t0 = time.time()
        from FlagEmbedding import FlagModel
        _embedding_model = FlagModel(
            "BAAI/bge-small-zh-v1.5",
            query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
            use_fp16=True
        )
        print(f"[NoteSearch] 模型加载完成 ({time.time() - t0:.1f}s)")
    return _embedding_model


def _load_embeddings_into_cache() -> bool:
    """从 MongoDB 加载所有笔记 embedding 到内存"""
    global _embedding_cache

    # 检查缓存是否有效
    if _embedding_cache["matrix"] is not None and _embedding_cache["loaded_at"]:
        age = (datetime.now() - _embedding_cache["loaded_at"]).total_seconds()
        if age < _embedding_cache["ttl_seconds"]:
            return True

    print("[NoteSearch] 从 MongoDB 加载笔记 embedding 到内存缓存...")
    t0 = time.time()

    repo = NoteEmbeddingRepository()
    all_notes = repo.get_all_embeddings()

    if not all_notes:
        print("[NoteSearch] 没有笔记 embedding 数据")
        _embedding_cache["note_ids"] = []
        _embedding_cache["matrix"] = np.array([])
        _embedding_cache["metadata"] = {}
        _embedding_cache["loaded_at"] = datetime.now()
        return False

    note_ids = []
    embeddings = []
    metadata = {}

    for note in all_notes:
        nid = note["note_id"]
        emb = note.get("embedding")
        if not emb or len(emb) == 0:
            continue

        note_ids.append(nid)
        embeddings.append(emb)
        metadata[nid] = {
            "note_id": nid,
            "user_id": note.get("user_id", ""),
            "title": note.get("title", ""),
            "desc": note.get("desc", ""),
            "likes": note.get("likes", 0),
            "collected_count": note.get("collected_count", 0),
            "comments_count": note.get("comments_count", 0),
            "share_count": note.get("share_count", 0),
            "engagement_score": note.get("engagement_score", 0.0),
            "nickname": note.get("nickname", ""),
            "avatar": note.get("avatar", ""),
            "note_create_time": note.get("note_create_time", 0),
        }

    matrix = np.array(embeddings, dtype=np.float32)
    # L2 归一化，方便后续用 dot product 计算 cosine similarity
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0  # 避免除零
    matrix = matrix / norms

    _embedding_cache["note_ids"] = note_ids
    _embedding_cache["matrix"] = matrix
    _embedding_cache["metadata"] = metadata
    _embedding_cache["loaded_at"] = datetime.now()

    print(f"[NoteSearch] 缓存加载完成: {len(note_ids)} 条笔记 ({time.time() - t0:.2f}s)")
    return True


def invalidate_cache():
    """手动清除缓存（新增笔记后调用）"""
    _embedding_cache["loaded_at"] = None
    _embedding_cache["matrix"] = None
    print("[NoteSearch] 缓存已清除")


# =====================================================
# 核心搜索函数
# =====================================================

def search_notes(
    query: str,
    top_k: int = 10,
    min_engagement: float = 0.0,
) -> Dict[str, Any]:
    """
    语义搜索笔记

    Args:
        query: 用户输入的搜索关键词/句子
        top_k: 返回前 K 条结果
        min_engagement: 最低互动指数过滤

    Returns:
        { "success": True, "results": [...], "query": "...", "total": N }
    """
    t_start = time.time()

    # 1. 加载缓存
    has_data = _load_embeddings_into_cache()
    if not has_data or len(_embedding_cache["note_ids"]) == 0:
        return {
            "success": True,
            "results": [],
            "query": query,
            "total": 0,
            "message": "暂无笔记 embedding 数据，请先运行 generate_note_embeddings.py"
        }

    # 2. 编码查询文本
    model = _get_embedding_model()
    query_vec = model.encode([query])  # shape (1, 512)
    query_vec = np.array(query_vec, dtype=np.float32)
    # L2 归一化
    norm = np.linalg.norm(query_vec)
    if norm > 0:
        query_vec = query_vec / norm

    # 3. 计算余弦相似度（因为已归一化，dot product == cosine similarity）
    matrix = _embedding_cache["matrix"]
    similarities = np.dot(matrix, query_vec.T).flatten()  # shape (N,)

    # 4. 获取 top-k 索引
    top_indices = np.argsort(similarities)[::-1][:top_k * 2]  # 取多一些用于过滤

    # 5. 组装结果
    results = []
    note_ids = _embedding_cache["note_ids"]
    metadata = _embedding_cache["metadata"]

    for idx in top_indices:
        if len(results) >= top_k:
            break

        nid = note_ids[idx]
        sim = float(similarities[idx])
        meta = metadata.get(nid, {})

        # 互动指数过滤
        if min_engagement > 0 and meta.get("engagement_score", 0) < min_engagement:
            continue

        results.append({
            **meta,
            "similarity": round(sim, 4),
        })

    t_elapsed = time.time() - t_start

    return {
        "success": True,
        "results": results,
        "query": query,
        "total": len(results),
        "search_time_ms": round(t_elapsed * 1000, 1),
        "index_size": len(note_ids),
    }


def get_note_stats() -> Dict[str, Any]:
    """获取笔记 embedding 统计信息"""
    repo = NoteEmbeddingRepository()
    stats = repo.get_stats()

    # 补充缓存状态
    cache_loaded = _embedding_cache["matrix"] is not None
    cache_size = len(_embedding_cache["note_ids"]) if cache_loaded else 0
    cache_age = None
    if _embedding_cache["loaded_at"]:
        cache_age = (datetime.now() - _embedding_cache["loaded_at"]).total_seconds()

    return {
        **stats,
        "cache": {
            "loaded": cache_loaded,
            "size": cache_size,
            "age_seconds": round(cache_age, 1) if cache_age else None,
            "ttl_seconds": _embedding_cache["ttl_seconds"],
        }
    }
