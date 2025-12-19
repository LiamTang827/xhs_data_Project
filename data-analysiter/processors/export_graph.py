import json
import glob
import os
import numpy as np
from pathlib import Path
import random

# Paths
BASE_DIR = Path(__file__).resolve().parent
PROFILES_DIR = BASE_DIR / "user_profiles"
ANALYSES_DIR = BASE_DIR / "analyses"
FRONTEND_DATA_FILE = BASE_DIR.parent / "xhs-analyser-frontend/src/data/creators.ts"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def cosine_similarity(v1, v2):
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return np.dot(v1, v2) / (norm1 * norm2)

def main():
    print("Starting graph data export...")
    
    # 1. Load User Profiles
    profiles = {}
    profile_files = glob.glob(str(PROFILES_DIR / "*.json"))
    
    nodes = []
    
    print(f"Found {len(profile_files)} profiles.")

    for pf in profile_files:
        data = load_json(pf)
        basic = data.get("user_basic", {})
        
        user_id = basic.get("user_id")
        nickname = basic.get("nickname")
        
        if not user_id:
            print(f"Skipping {pf}: No user_id")
            continue
            
        # Extract fields
        fans = basic.get("fans", 0)
        if isinstance(fans, str):
            fans = 0 # Handle parsing if needed
            
        interaction = basic.get("interaction", 0)
        if isinstance(interaction, str):
            interaction = 0
            
        topics = data.get("content_topics", ["其他"])
        primary_track = topics[0] if topics else "其他"
        
        style = data.get("content_style", {})
        if isinstance(style, dict):
            content_form = style.get("语言风格", "未知")
        elif isinstance(style, list):
            content_form = ", ".join([str(s) for s in style]) if style else "未知"
        else:
            content_form = "未知"
        
        tags = basic.get("tag_list", {})
        keywords = list(tags.values()) if isinstance(tags, dict) else []
        
        # Random position for now (frontend simulation will adjust)
        pos_x = random.randint(0, 100)
        pos_y = random.randint(0, 100)
        
        node = {
            "id": user_id,
            "name": nickname,
            "followers": fans,
            "engagementIndex": interaction, # Simple normalization
            "primaryTrack": primary_track,
            "contentForm": content_form,
            "recentKeywords": keywords,
            "position": {"x": pos_x, "y": pos_y},
            "avatar": basic.get("avatar", ""),
            "desc": basic.get("desc", ""),
            "ipLocation": basic.get("ip_location", "")
        }
        
        nodes.append(node)
        profiles[nickname] = node # Map nickname to node for embedding matching if needed
        profiles[user_id] = node

    # 2. Load Embeddings and Compute Edges
    embedding_files = glob.glob(str(ANALYSES_DIR / "*__embedding.json"))
    embeddings = {}
    
    print(f"Found {len(embedding_files)} embedding files.")

    for ef in embedding_files:
        data = load_json(ef)
        # Filename format: Nickname__embedding.json
        # We need to map this back to user_id
        filename = Path(ef).name
        nickname_part = filename.replace("__embedding.json", "")
        
        # Find user_id by nickname
        found_node = None
        for n in nodes:
            if n["name"] == nickname_part:
                found_node = n
                break
        
        if found_node:
            embeddings[found_node["id"]] = np.array(data["embedding"])
        else:
            print(f"Warning: No profile found for embedding {nickname_part}")

    edges = []
    user_ids = list(embeddings.keys())
    
    for i in range(len(user_ids)):
        for j in range(i + 1, len(user_ids)):
            uid1 = user_ids[i]
            uid2 = user_ids[j]
            
            vec1 = embeddings[uid1]
            vec2 = embeddings[uid2]
            
            sim = cosine_similarity(vec1, vec2)
            
            if sim > 0.7: # Threshold
                edges.append({
                    "source": uid1,
                    "target": uid2,
                    "weight": round(float(sim), 2),
                    "types": {"style": 1} # Dummy type
                })

    # 3. Generate Track Clusters
    track_clusters = {}
    for n in nodes:
        track = n["primaryTrack"]
        if track not in track_clusters:
            track_clusters[track] = []
        track_clusters[track].append(n["id"])

    # 4. Write TypeScript File
    now_str = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    ts_content = f"""// 此文件由脚本自动生成
// 生成时间: {now_str}
// 数据来源: data-analysiter

export interface CreatorNode {{
  id: string;
  name: string;
  followers: number;
  engagementIndex: number;
  primaryTrack: string;
  contentForm: string;
  recentKeywords: string[];
  position: {{ x: number; y: number }};
  avatar?: string;
  ipLocation?: string;
  desc?: string;
  redId?: string;
}}

export type CreatorEdgeSignal = "keyword" | "audience" | "style" | "campaign";

export interface CreatorEdge {{
  source: string;
  target: string;
  weight: number;
  types: Partial<Record<CreatorEdgeSignal, number>>;
  sampleEvents?: Array<{{
    type: CreatorEdgeSignal;
    title: string;
    timestamp: string;
  }}>;
}}

export const creators: CreatorNode[] = {json.dumps(nodes, ensure_ascii=False, indent=2)};

export const creatorEdges: CreatorEdge[] = {json.dumps(edges, ensure_ascii=False, indent=2)};

export const trackClusters: Record<string, string[]> = {json.dumps(track_clusters, ensure_ascii=False, indent=2)};

export const trendingKeywordGroups: Array<{{
  topic: string;
  creators: string[];
  intensity: number;
}}> = [];
"""

    # Fix JSON output to match TS object syntax slightly better if needed, 
    # but valid JSON is valid JS/TS object literal (mostly).
    # We might need to remove quotes from keys if strict TS linting complains, 
    # but usually JSON is fine.
    
    with open(FRONTEND_DATA_FILE, "w", encoding="utf-8") as f:
        f.write(ts_content)
        
    print(f"Successfully wrote {len(nodes)} nodes and {len(edges)} edges to {FRONTEND_DATA_FILE}")

if __name__ == "__main__":
    import datetime
    main()
