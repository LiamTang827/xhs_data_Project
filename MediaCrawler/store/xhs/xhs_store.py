import os
import json
import pathlib
from typing import Dict, List
import aiofiles
from tools import utils

async def save_creator(user_id: str, creator: Dict):
    """Save creator info to json file"""
    if not creator:
        return
    
    # Define the path to save the creator's information
    storage_dir = "data/xhs/creator"
    pathlib.Path(storage_dir).mkdir(parents=True, exist_ok=True)
    storage_path = f"{storage_dir}/{user_id}.json"
    
    # Write the creator data to file
    async with aiofiles.open(storage_path, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(creator, ensure_ascii=False, indent=4))
    
    utils.logger.info(f"[store.xhs.save_creator] Saved creator info for user_id: {user_id} to {storage_path}")

async def update_xhs_note(note_item: Dict):
    """Update xhs note to json file"""
    if not note_item:
        return
    note_id = note_item.get("note_id")
    if not note_id:
        return
    
    # Define the path to save the note information
    storage_dir = "data/xhs/notes"
    pathlib.Path(storage_dir).mkdir(parents=True, exist_ok=True)
    storage_path = f"{storage_dir}/{note_id}.json"
    
    # Write the note data to file
    async with aiofiles.open(storage_path, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(note_item, ensure_ascii=False, indent=4))
    
    utils.logger.info(f"[store.xhs.update_xhs_note] Saved note info for note_id: {note_id} to {storage_path}")

async def batch_update_xhs_notes(note_list: List[Dict]):
    """Batch update xhs notes to json file"""
    for note_item in note_list:
        await update_xhs_note(note_item)

async def update_xhs_note_comment(note_id: str, comments: List[Dict]):
    """Update xhs note comment to json file"""
    if not comments:
        return
    
    # Define the path to save the comments
    storage_dir = "data/xhs/comments"
    pathlib.Path(storage_dir).mkdir(parents=True, exist_ok=True)
    storage_path = f"{storage_dir}/{note_id}.json"
    
    # Write the comments data to file
    async with aiofiles.open(storage_path, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(comments, ensure_ascii=False, indent=4))
    
    utils.logger.info(f"[store.xhs.update_xhs_note_comment] Saved comments for note_id: {note_id} to {storage_path}")
