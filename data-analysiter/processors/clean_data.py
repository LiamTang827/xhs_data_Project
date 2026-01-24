#!/usr/bin/env python3
"""Simple data cleaner for xhs_users and xhs_notes.

Usage examples:
  # clean single user and its notes, print to stdout
  python3 clean_data.py --user_id 66d6aedc000000001e00f94d

  # clean all users and save to JSONL files
  python3 clean_data.py --out-json users_clean.jsonl notes_clean.jsonl

  # clean all and upsert into collections xhs_users_clean / xhs_notes_clean
  python3 clean_data.py --save-to-db

The script keeps only the target fields described in the request and normalizes types.
"""

import os
import json
import argparse
from datetime import datetime
from urllib.parse import urlparse
from pymongo import MongoClient
from bson import ObjectId
import re
import pathlib
from dotenv import load_dotenv
from pathlib import Path

# 加载 data-analysiter 目录的 .env 文件
load_dotenv(Path(__file__).parent.parent / '.env')

DEFAULT_URI = os.environ.get("MONGO_URI")
if not DEFAULT_URI:
    raise ValueError("MONGO_URI environment variable is required")
DEFAULT_DB = os.environ.get("DATABASE_NAME", "tikhub_xhs")


def to_int(v, default=0):
    try:
        return int(v)
    except Exception:
        try:
            return int(float(v))
        except Exception:
            return default


def valid_url(s: str) -> bool:
    if not s or not isinstance(s, str):
        return False
    try:
        p = urlparse(s)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


def normalize_tag_list_for_user(val):
    """User tag_list: prefer dict (info/location etc.).
    Accept dict, list, string. Return dict or None.
    """
    if val is None:
        return None
    if isinstance(val, dict):
        return {k: str(v) for k, v in val.items() if v is not None}
    if isinstance(val, list):
        # convert to keyed dict idx->value
        return {str(i): str(v) for i, v in enumerate(val) if v is not None}
    if isinstance(val, str):
        # try parse as JSON list/dict
        try:
            parsed = json.loads(val)
            return normalize_tag_list_for_user(parsed)
        except Exception:
            parts = [p.strip() for p in re_split_tags(val)]
            return {str(i): p for i, p in enumerate(parts) if p}


def normalize_tag_list_for_note(val):
    """Note tag_list: return list of strings or []"""
    if val is None:
        return []
    if isinstance(val, list):
        return [str(x).strip() for x in val if x]
    if isinstance(val, dict):
        # dict of {k:v} -> use values
        return [str(v).strip() for v in val.values() if v]
    if isinstance(val, str):
        try:
            parsed = json.loads(val)
            return normalize_tag_list_for_note(parsed)
        except Exception:
            return [p.strip() for p in re_split_tags(val) if p.strip()]


def re_split_tags(s: str):
    # split by common separators
    for sep in [",", "，", ";", "；", "|", " "]:
        if sep in s:
            return [p for p in s.split(sep) if p.strip()]
    return [s]


def normalize_image_list(val):
    if val is None:
        return []
    if isinstance(val, list):
        return [u for u in val if isinstance(u, str) and valid_url(u)]
    if isinstance(val, str):
        # try JSON
        try:
            parsed = json.loads(val)
            return normalize_image_list(parsed)
        except Exception:
            # split heuristically
            parts = [p.strip() for p in val.split(",") if p.strip()]
            return [p for p in parts if valid_url(p)]
    return []


def normalize_video_url(val):
    if not val:
        return None
    if isinstance(val, str) and valid_url(val):
        return val
    # if dict/other, try to find url-like field
    if isinstance(val, dict):
        for k in ("url", "video_url", "src"):
            if k in val and isinstance(val[k], str) and valid_url(val[k]):
                return val[k]
    return None


def normalize_time(val):
    """Normalize timestamps to integer milliseconds since epoch.
    Accept ms (13-digit), seconds (10-digit), datetime objects, or ISO strings.
    """
    if val is None:
        return None
    # datetime
    if isinstance(val, datetime):
        return int(val.timestamp() * 1000)
    # int-like
    try:
        n = int(val)
        # if looks like seconds (10 digits), convert
        if n < 10**11:
            return n * 1000
        return n
    except Exception:
        pass
    # string ISO
    try:
        dt = datetime.fromisoformat(str(val))
        return int(dt.timestamp() * 1000)
    except Exception:
        return None


def clean_user(doc):
    if not doc:
        return None
    return {
        "user_id": str(doc.get("user_id") or doc.get("userid") or doc.get("_id") or ""),
        "nickname": doc.get("nickname") or doc.get("name") or None,
        "avatar": doc.get("avatar") if valid_url(doc.get("avatar")) else None,
        "desc": doc.get("desc") or doc.get("description") or None,
        "fans": to_int(doc.get("fans") or doc.get("fan_count"), 0),
        "interaction": to_int(doc.get("interaction") or doc.get("interact_count"), 0),
        "tag_list": normalize_tag_list_for_user(doc.get("tag_list")),
        "gender": (doc.get("gender") or "未知"),
        "ip_location": doc.get("ip_location") or doc.get("location") or None,
    }


def clean_note(doc):
    if not doc:
        return None
    
    # 提取user_id（从note中的user对象或直接字段）
    user_id = ""
    if "user" in doc and isinstance(doc["user"], dict):
        user_id = str(doc["user"].get("userid") or doc["user"].get("user_id") or "")
    else:
        user_id = str(doc.get("user_id") or doc.get("userid") or doc.get("uid") or "")
    
    return {
        "note_id": str(doc.get("note_id") or doc.get("id") or doc.get("_id") or ""),
        "user_id": user_id,
        "title": doc.get("title") or doc.get("display_title") or None,
        "desc": doc.get("desc") or doc.get("description") or None,
        "image_list": normalize_image_list(doc.get("image_list") or doc.get("images_list") or doc.get("images")),
        "video_url": normalize_video_url(doc.get("video_url") or doc.get("video") or doc.get("video_src")),
        "liked_count": to_int(doc.get("liked_count") or doc.get("nice_count") or doc.get("likes") or 0),
        "collected_count": to_int(doc.get("collected_count") or doc.get("collects") or 0),
        "comment_count": to_int(doc.get("comment_count") or doc.get("comments_count") or doc.get("comments") or 0),
        "share_count": to_int(doc.get("share_count") or doc.get("shares") or 0),
        "tag_list": normalize_tag_list_for_note(doc.get("tag_list") or doc.get("tags")),
        "time": normalize_time(doc.get("time") or doc.get("create_time") or doc.get("created_at")),
        "note_url": doc.get("note_url") if valid_url(doc.get("note_url")) else None,
    }


def process_from_mongo(uri, db_name, user_id=None, out_json=None, save_to_db=False, notes_limit=0):
    client = MongoClient(uri)
    db = client[db_name]
    
    # 优先从 user_snapshots 读取（新架构）
    snapshots_coll = db["user_snapshots"]
    # 兼容旧架构
    users_coll = db["xhs_users"]
    notes_coll = db["xhs_notes"]

    users_out = []
    notes_out = []

    if user_id:
        # 先尝试从 user_snapshots 获取
        snapshot_doc = snapshots_coll.find_one({"user_id": user_id})
        
        if snapshot_doc:
            # 从 snapshot 提取 user 和 notes
            notes = snapshot_doc.get('notes', [])
            
            # 从第一条 note 提取 user 信息（如果有）
            user_info = None
            if notes and 'user' in notes[0]:
                user_info = notes[0]['user']
            
            # 构建 user 对象
            if user_info:
                cu = clean_user(user_info)
            else:
                # 如果没有user信息，从snapshot本身构建基础信息
                cu = {
                    "user_id": user_id,
                    "nickname": None,
                    "avatar": None,
                    "desc": None,
                    "fans": 0,
                    "interaction": 0,
                    "tag_list": None,
                    "gender": "未知",
                    "ip_location": None,
                }
            users_out.append(cu)
            
            # 清洗 notes
            if notes_limit and notes_limit > 0:
                notes = notes[:notes_limit]
            for n in notes:
                notes_out.append(clean_note(n))
        else:
            # 兼容旧架构：从 xhs_users 查找
            user_doc = users_coll.find_one({"user_id": user_id}) or users_coll.find_one({"_id": try_objectid(user_id)})
            if not user_doc:
                print(f"User {user_id} not found in user_snapshots or xhs_users")
                client.close()
                return
            cu = clean_user(user_doc)
            users_out.append(cu)
            q = {"user_id": user_id}
            cursor = notes_coll.find(q).sort("create_time", -1)
            if notes_limit and notes_limit > 0:
                cursor = cursor.limit(notes_limit)
            for n in cursor:
                notes_out.append(clean_note(n))
    else:
        # 处理所有用户：优先从 snapshots
        snapshot_cursor = snapshots_coll.find({})
        for snap in snapshot_cursor:
            notes = snap.get('notes', [])
            if notes and 'user' in notes[0]:
                users_out.append(clean_user(notes[0]['user']))
            for n in notes:
                notes_out.append(clean_note(n))
        
        # 如果没有snapshots，兼容旧架构
        if not users_out:
            cursor = users_coll.find({})
            for u in cursor:
                users_out.append(clean_user(u))
            cursor2 = notes_coll.find({}).sort("create_time", -1)
            if notes_limit and notes_limit > 0:
                cursor2 = cursor2.limit(notes_limit)
            for n in cursor2:
                notes_out.append(clean_note(n))

    if out_json:
        users_path, notes_path = out_json
        with open(users_path, "w", encoding="utf-8") as f:
            for u in users_out:
                f.write(json.dumps(u, ensure_ascii=False) + "\n")
        with open(notes_path, "w", encoding="utf-8") as f:
            for n in notes_out:
                f.write(json.dumps(n, ensure_ascii=False) + "\n")
        print(f"Wrote {len(users_out)} users to {users_path}, {len(notes_out)} notes to {notes_path}")

    if save_to_db:
        u_coll = db.get_collection("xhs_users_clean")
        n_coll = db.get_collection("xhs_notes_clean")
        upserted = 0
        for u in users_out:
            u_coll.replace_one({"user_id": u["user_id"]}, u, upsert=True)
            upserted += 1
        for n in notes_out:
            n_coll.replace_one({"note_id": n["note_id"]}, n, upsert=True)
        print(f"Upserted {upserted} users and {len(notes_out)} notes into {db_name}")

    if not out_json and not save_to_db and user_id:
        # 自动保存为snapshot文件到 data/snapshots/ 目录
        snapshot_dir = pathlib.Path(__file__).resolve().parent.parent / "data" / "snapshots"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        user = users_out[0] if users_out else None
        if user:
            snapshot = {
                "snapshot_time": datetime.utcnow().replace(microsecond=0).isoformat(),
                "user": user,
                "notes": notes_out
            }
            
            # 生成文件名
            nickname = user.get("nickname") or user.get("user_id") or "snapshot"
            safe_name = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "_", nickname).strip("_")
            date_str = datetime.utcnow().strftime("%Y-%m-%d")
            file_name = f"{safe_name}_{date_str}.json"
            out_path = snapshot_dir / file_name
            
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 已保存snapshot: {out_path}")
    
    elif not out_json and not save_to_db:
        # 没有指定user_id，只打印到stdout
        print("Users:")
        for u in users_out:
            print(json.dumps(u, ensure_ascii=False))
        print("\nNotes:")
        for n in notes_out:
            print(json.dumps(n, ensure_ascii=False))

    # Return cleaned objects for snapshot generation or calling code
    client.close()
    return {"user": (users_out[0] if users_out else None), "notes": notes_out}


def try_objectid(s):
    try:
        return ObjectId(s)
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Clean xhs user/note data")
    parser.add_argument("--user_id", help="Only process this user_id (optional)")
    parser.add_argument("--db", default=DEFAULT_DB, help="MongoDB database name")
    parser.add_argument("--uri", default=DEFAULT_URI, help="MongoDB URI")
    parser.add_argument("--out-json", nargs=2, metavar=("USERS_JSON", "NOTES_JSON"), help="Output JSONL file paths")
    parser.add_argument("--save-to-db", action="store_true", help="Save cleaned docs to xhs_users_clean/xhs_notes_clean collections")
    parser.add_argument("--notes-limit", type=int, default=0, help="Limit number of notes to process (0 = all)")

    args = parser.parse_args()
    # If no args provided, run a demo for the test user_id and print results.
    # This makes running `python3 clean_data.py` show the expected demo output.


    if not any([args.user_id, args.out_json, args.save_to_db, args.notes_limit]):
        demo_id = "5ff98b9d0000000001008f40"
        print(f"No args detected — running demo for user_id={demo_id}\n")
        result = process_from_mongo(args.uri, args.db, user_id=demo_id, out_json=None, save_to_db=False, notes_limit=20)

        # Build snapshot and write to snapshots/ directory
        snapshot_dir = pathlib.Path(__file__).resolve().parent / "snapshots"
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        user = result.get("user")
        notes = result.get("notes")

        # helper to pick last_modify_ts/last_update_time from raw note docs
        def pick_ts(raw, candidates):
            for k in candidates:
                if k in raw and raw[k] is not None:
                    ts = normalize_time(raw[k])
                    if ts:
                        return ts
            return None

        # attempt to add last_modify_ts/last_update_time if original raw docs had them
        # Note: process_from_mongo returns cleaned dicts; we can try to fetch originals again for timestamps
        # For simplicity, use fields already present in cleaned objects if available
        if user:
            # try to copy last_modify_ts from the original DB if present
            # we will attempt to re-query original to get raw timestamps
            raw_user = None
            try:
                client2 = MongoClient(args.uri)
                raw_user = client2[args.db]["xhs_users"].find_one({"user_id": user.get("user_id")})
            except Exception:
                raw_user = None
            finally:
                try:
                    client2.close()
                except Exception:
                    pass

            last_modify = None
            if raw_user:
                last_modify = pick_ts(raw_user, ["last_modify_ts", "last_modified", "modified_at", "update_time", "updated_at"]) 
            user["last_modify_ts"] = last_modify

        # For notes, try to get last_modify_ts and last_update_time from raw docs
        raw_notes_map = {}
        try:
            client3 = MongoClient(args.uri)
            cursor_raw = client3[args.db]["xhs_notes"].find({"user_id": user.get("user_id")})
            for rn in cursor_raw:
                raw_notes_map[str(rn.get("note_id") or rn.get("_id"))] = rn
        except Exception:
            raw_notes_map = {}
        finally:
            try:
                client3.close()
            except Exception:
                pass

        snapshot_notes = []
        for n in notes:
            rn = raw_notes_map.get(n.get("note_id"))
            last_modify = pick_ts(rn, ["last_modify_ts", "last_modified", "modified_at", "update_time", "updated_at"]) if rn else None
            last_update = pick_ts(rn, ["last_update_time", "last_update", "updated_at", "update_time"]) if rn else None
            # attach if available
            if last_modify:
                n["last_modify_ts"] = last_modify
            else:
                n["last_modify_ts"] = None
            if last_update:
                n["last_update_time"] = last_update
            else:
                n["last_update_time"] = None
            # try to copy ip_location if present in raw
            if rn and rn.get("ip_location"):
                n["ip_location"] = rn.get("ip_location")
            snapshot_notes.append(n)

        snapshot = {
            "snapshot_time": datetime.utcnow().replace(microsecond=0).isoformat(),
            "user": user,
            "notes": snapshot_notes,
        }

        # sanitize filename from nickname
        nickname = (user.get("nickname") or user.get("user_id") or "snapshot")
        safe_name = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "_", nickname).strip("_")
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        file_name = f"{safe_name}_{date_str}.json"
        out_path = snapshot_dir / file_name
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)
        print(f"Snapshot written to: {out_path}\n")
    else:
        process_from_mongo(args.uri, args.db, user_id=args.user_id, out_json=args.out_json, save_to_db=args.save_to_db, notes_limit=args.notes_limit)


if __name__ == "__main__":
    main()
