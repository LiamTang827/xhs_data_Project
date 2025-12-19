#!/usr/bin/env python3
"""Insert test documents into MongoDB for verification.

This script will:
- try to load environment variables from `spider-api/.env` (if present)
- add the MediaCrawler package to `sys.path` so local imports work
- connect using `MongoDBConnection` from `database/mongodb_store_base.py`
- insert one document into `xhs_notes` and one into `xhs_users`
- print inserted ids or a descriptive error

Run from repository root (recommended):
  cd /path/to/xhs_data_Project
  export $(egrep -v '^#' spider-api/.env | xargs)
  python3 MediaCrawler/scripts/insert_mongo_test.py

Or simply run without exporting; the script will attempt to load `spider-api/.env` itself.
"""

import asyncio
import pathlib
import os
import sys
import time
import traceback

ROOT = pathlib.Path(__file__).resolve().parents[1]
ENV_PATH = ROOT.parent / "spider-api" / ".env"

# Try to load .env if exists (simple parser so python-dotenv not required)
if ENV_PATH.exists():
    try:
        text = ENV_PATH.read_text(encoding="utf-8")
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k, v)
    except Exception:
        print("Warning: failed to read spider-api/.env, continuing with current env")

# Ensure MediaCrawler package is importable
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

async def main():
    try:
        from database.mongodb_store_base import MongoDBConnection
    except Exception as e:
        print("Failed to import MongoDBConnection:", e)
        traceback.print_exc()
        return

    conn = MongoDBConnection()
    try:
        db = await conn.get_db()
        print("Connected to MongoDB database:", getattr(db, 'name', '<unknown>'))

        now = time.time()
        note = {"_test": "ok", "ts": now}
        user = {"_test_user": "ok", "ts": now}

        # Insert into collections with existing prefix logic (MongoDBStoreBase uses prefix + '_' + suffix)
        # Default prefix for XHS store is 'xhs', so collections will be 'xhs_notes' and 'xhs_users'
        r1 = await db['xhs_notes'].insert_one(note)
        r2 = await db['xhs_users'].insert_one(user)

        print('Inserted test docs:')
        print('  xhs_notes id ->', r1.inserted_id)
        print('  xhs_users id ->', r2.inserted_id)
    except Exception as e:
        print('Mongo insert failed:', repr(e))
        traceback.print_exc()
    finally:
        try:
            await conn.close()
        except Exception:
            pass

if __name__ == '__main__':
    asyncio.run(main())
