import os
import json
import argparse
from pathlib import Path
import numpy as np
from FlagEmbedding import FlagModel

MODEL_NAME = "BAAI/bge-small-zh-v1.5"  # 你当前的模型
# query_instruction_for_retrieval 可选，用于增强检索向量语义
MODEL_ARGS = {"query_instruction_for_retrieval": "为这个句子生成表示以用于检索相关文章：", "use_fp16": True}

def build_text_from_profile(profile: dict) -> str:
    parts = []
    ub = profile.get("user_basic", {})
    if ub.get("nickname"):
        parts.append(f"Nickname: {ub.get('nickname')}")
    if ub.get("desc"):
        parts.append(f"Desc: {ub.get('desc')}")
    topics = profile.get("content_topics") or []
    if topics:
        parts.append("Topics: " + ", ".join(topics))
    style = profile.get("content_style") or {}
    if style:
        parts.append("Style: " + json.dumps(style, ensure_ascii=False))
    vp = profile.get("value_points") or []
    if vp:
        parts.append("Value Points: " + "; ".join(vp))
    return "\n\n".join(parts)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="单个 profile 文件，或省略以处理目录内全部", default=None)
    parser.add_argument("--out", help="输出目录", default="analyses")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    profiles_dir = root / "user_profiles"
    out_dir = root / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    model = FlagModel(MODEL_NAME, **MODEL_ARGS)

    if args.input:
        files = [Path(args.input)]
    else:
        files = sorted(profiles_dir.glob("*.json"))

    for p in files:
        print("Processing", p.name)
        with open(p, "r", encoding="utf-8") as f:
            profile = json.load(f)
        text = build_text_from_profile(profile)
        # encode 接受 list
        vec = model.encode([text])  # 返回 numpy array shape (1, dim)
        if hasattr(vec, "tolist"):
            emb = vec.tolist()[0]
        else:
            emb = np.array(vec).tolist()
        out_path = out_dir / (p.stem + "__embedding.json")
        with open(out_path, "w", encoding="utf-8") as fo:
            json.dump({"source": p.name, "embedding": emb}, fo, ensure_ascii=False)
        print("Saved", out_path)

if __name__ == "__main__":
    main()