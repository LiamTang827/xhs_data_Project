#!/usr/bin/env python3
"""
Data Analysis Pipeline
----------------------
Orchestrates the flow:
1. MongoDB -> Snapshots (clean_data.py)
2. Snapshots -> User Profiles (LLM Analysis)
3. User Profiles -> Embeddings (Deepseek/OpenAI)
4. Profiles + Embeddings -> Graph Data (export_graph_data.py) -> Frontend

Usage:
    python3 pipeline.py --user_id <id>   # Process specific user
    python3 pipeline.py                  # Process all users found in DB
"""

import os
import json
import glob
import re
import argparse
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# Import local modules
# Ensure we can import from current directory
import sys
sys.path.append(str(Path(__file__).resolve().parent))

from clean_data import process_from_mongo
import export_graph_data

# Configuration
# Use env vars or fallback to the key user provided in test_api.py
API_KEY = os.environ.get("DEEPSEEK_API_KEY") or "sk-fc8855de5f0f4bfd9760e03bcd67e2ef"
BASE_URL = os.environ.get("DEEPSEEK_BASE_URL") or "https://api.deepseek.com"

BASE_DIR = Path(__file__).resolve().parent
SNAPSHOTS_DIR = BASE_DIR / "snapshots"
PROFILES_DIR = BASE_DIR / "user_profiles"
ANALYSES_DIR = BASE_DIR / "analyses"

SNAPSHOTS_DIR.mkdir(exist_ok=True)
PROFILES_DIR.mkdir(exist_ok=True)
ANALYSES_DIR.mkdir(exist_ok=True)

# Initialize OpenAI client for Deepseek
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def step_fetch_snapshots(user_id=None):
    print("\n--- Step 1: Fetching Snapshots from MongoDB ---")
    
    # We need to list users first to iterate them
    from pymongo import MongoClient
    # Use URI from clean_data or default
    uri = "mongodb+srv://xhs_user:S8VVePhiUHfT6H5U@xhs-cluster.omeyngi.mongodb.net/?retryWrites=true&w=majority&appName=xhs-Cluster"
    db_name = "media_crawler"
    
    try:
        client_mongo = MongoClient(uri)
        db = client_mongo[db_name]
        users_coll = db["xhs_users"]
        
        query = {}
        if user_id:
            query = {"user_id": user_id}
            
        # Get list of user_ids to process
        # We use a projection to be efficient
        cursor = users_coll.find(query, {"user_id": 1, "nickname": 1, "name": 1})
        users_list = list(cursor)
        client_mongo.close()
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return

    print(f"Found {len(users_list)} users to process.")
    
    for u_doc in users_list:
        uid = u_doc.get("user_id")
        nickname = u_doc.get("nickname") or u_doc.get("name") or uid
        
        if not uid:
            continue
            
        print(f"Processing snapshot for: {nickname} ({uid})")
        
        # Use clean_data logic to get cleaned object
        # We limit notes to 20 to avoid huge contexts for LLM
        try:
            result = process_from_mongo(uri, db_name, user_id=uid, notes_limit=20)
        except Exception as e:
            print(f"Error cleaning data for {uid}: {e}")
            continue
        
        if not result or not result.get("user"):
            print(f"No valid data found for {uid}")
            continue
            
        # Create snapshot structure
        snapshot = {
            "snapshot_time": datetime.utcnow().replace(microsecond=0).isoformat(),
            "user": result["user"],
            "notes": result["notes"]
        }
        
        # Save
        safe_name = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "_", str(nickname)).strip("_")
        if not safe_name: safe_name = str(uid)
        
        # We use a fixed filename pattern so we can find it later easily
        # For pipeline simplicity, we might overwrite the latest snapshot for this user
        # or append date. Let's append date.
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        filename = f"{safe_name}_{date_str}.json"
        save_json(SNAPSHOTS_DIR / filename, snapshot)
        print(f"Saved snapshot: {filename}")

def step_generate_profiles():
    print("\n--- Step 2: Generating User Profiles (LLM) ---")
    snapshot_files = glob.glob(str(SNAPSHOTS_DIR / "*.json"))
    
    if not snapshot_files:
        print("No snapshots found.")
        return

    for sf in snapshot_files:
        path = Path(sf)
        data = load_json(path)
        
        user_info = data.get("user", {})
        nickname = user_info.get("nickname") or user_info.get("user_id")
        if not nickname: continue

        safe_name = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "_", str(nickname)).strip("_")
        profile_path = PROFILES_DIR / f"{safe_name}.json"
        
        # Skip if profile exists to save API tokens (remove this check to force update)
        if profile_path.exists():
            print(f"Profile exists for {nickname}, skipping LLM call.")
            continue
            
        print(f"Generating profile for {nickname}...")
        
        # Prepare prompt
        snapshot_str = json.dumps(data, ensure_ascii=False)
        if len(snapshot_str) > 60000: # Truncate to avoid context limit
            snapshot_str = snapshot_str[:60000] + "...(truncated)"
            
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are an analyst. Always reply in strict JSON with fields: user_basic, content_topics, content_style, audience, value_points, content_clusters."},
                    {"role": "user", "content": "here is the user data and notes snapshots: " + snapshot_str + " Please analyze and summarize,and generate user profile."},
                ],
                stream=False
            )
            content = response.choices[0].message.content
            # Clean markdown code blocks
            content = content.replace("```json", "").replace("```", "").strip()
            
            profile_json = json.loads(content)
            
            # Ensure user_basic has user_id for linking
            if "user_basic" not in profile_json:
                profile_json["user_basic"] = {}
            
            # Merge basic info from snapshot if missing
            if "user_id" not in profile_json["user_basic"]:
                profile_json["user_basic"]["user_id"] = user_info.get("user_id")
            if "nickname" not in profile_json["user_basic"]:
                profile_json["user_basic"]["nickname"] = nickname
            
            # Save
            save_json(profile_path, profile_json)
            print(f"Saved profile: {profile_path.name}")
            
        except Exception as e:
            print(f"Error generating profile for {nickname}: {e}")

def step_generate_embeddings():
    print("\n--- Step 3: Generating Embeddings ---")
    profile_files = glob.glob(str(PROFILES_DIR / "*.json"))
    
    if not profile_files:
        print("No profiles found.")
        return

    for pf in profile_files:
        path = Path(pf)
        safe_name = path.stem
        embed_path = ANALYSES_DIR / f"{safe_name}__embedding.json"
        
        if embed_path.exists():
            print(f"Embedding exists for {safe_name}, skipping.")
            continue
            
        print(f"Generating embedding for {safe_name}...")
        profile = load_json(path)
        
        # Build text representation
        parts = []
        ub = profile.get("user_basic", {})
        if ub.get("nickname"): parts.append(f"Nickname: {ub.get('nickname')}")
        if ub.get("desc"): parts.append(f"Desc: {ub.get('desc')}")
        
        topics = profile.get("content_topics") or []
        if isinstance(topics, list):
            parts.append("Topics: " + ", ".join([str(t) for t in topics]))
            
        style = profile.get("content_style") or {}
        if isinstance(style, dict):
            parts.append("Style: " + json.dumps(style, ensure_ascii=False))
        elif isinstance(style, list):
            parts.append("Style: " + ", ".join([str(s) for s in style]))
            
        vp = profile.get("value_points") or []
        if isinstance(vp, list):
            parts.append("Value Points: " + "; ".join([str(v) for v in vp]))
        
        text = "\n\n".join(parts)
        
        try:
            resp = client.embeddings.create(model="text-embedding-3-small", input=[text])
            
            # Handle SDK response variations
            embedding = None
            if hasattr(resp, "data") and isinstance(resp.data, list) and resp.data:
                embedding = resp.data[0].embedding
            elif isinstance(resp, dict) and "data" in resp:
                embedding = resp["data"][0]["embedding"]
            else:
                # Fallback for some proxies
                try:
                    embedding = resp.data[0].embedding
                except:
                    pass
            
            if embedding:
                save_json(embed_path, {"source": path.name, "embedding": embedding})
                print(f"Saved embedding: {embed_path.name}")
            else:
                print(f"Failed to extract embedding for {safe_name}")
                
        except Exception as e:
            print(f"Error generating embedding for {safe_name}: {e}")

def step_export_graph():
    print("\n--- Step 4: Exporting Graph Data ---")
    try:
        export_graph_data.main()
    except Exception as e:
        print(f"Error exporting graph: {e}")

def main():
    parser = argparse.ArgumentParser(description="Run the full data analysis pipeline.")
    parser.add_argument("--user_id", help="Run for a specific user ID only")
    parser.add_argument("--skip-fetch", action="store_true", help="Skip fetching snapshots")
    parser.add_argument("--skip-profile", action="store_true", help="Skip generating profiles")
    parser.add_argument("--skip-embed", action="store_true", help="Skip generating embeddings")
    
    args = parser.parse_args()
    
    if not args.skip_fetch:
        step_fetch_snapshots(args.user_id)
    
    if not args.skip_profile:
        step_generate_profiles()
        
    if not args.skip_embed:
        step_generate_embeddings()
        
    step_export_graph()
    print("\nPipeline completed successfully!")

if __name__ == "__main__":
    main()
