#!/usr/bin/env python3
"""Verify MongoDB connectivity using MONGO_URI or db_config fallback.

This script:
- loads .env from project root and spider-api/.env (supports python-dotenv if installed)
- falls back to a simple parser if python-dotenv is missing
- inserts project root to sys.path so local imports work
- attempts to connect via MediaCrawler's MongoDBConnection
- prints DB name and a sample of collections

Run from repository root or MediaCrawler directory.
"""
import asyncio
import pathlib
import os
import sys
import traceback

ROOT = pathlib.Path(__file__).resolve().parents[1]
env_paths = [ROOT / '.env', ROOT / 'spider-api' / '.env']

# Try to load using python-dotenv if available; otherwise use a simple parser
try:
    from dotenv import load_dotenv
    for p in env_paths:
        if p.exists():
            load_dotenv(p)
except Exception:
    for p in env_paths:
        if p.exists():
            try:
                text = p.read_text(encoding='utf-8')
            except Exception:
                continue
            for line in text.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    continue
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k, v)

# Ensure project root is in sys.path so `import database` works
project_root = str(ROOT)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

async def main():
    try:
        from database.mongodb_store_base import MongoDBConnection
    except Exception as e:
        print("Failed to import MongoDBConnection from local package 'database':", e)
        traceback.print_exc()
        return

    try:
        conn = MongoDBConnection()
        db = await conn.get_db()
        print("Connected to MongoDB database:", db.name)
        try:
            coll_names = await db.list_collection_names()
            print("Collections (sample):", coll_names[:20])
        except Exception as e:
            print("Failed to list collections:", e)
        await conn.close()
    except Exception as e:
        print("MongoDB connection failed:", repr(e))
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
