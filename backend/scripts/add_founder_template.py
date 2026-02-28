#!/usr/bin/env python3
"""
Add the founder social media content template to the database
"""
from database.connection import get_database

def add_founder_template():
    db = get_database()
    
    # Check if template already exists
    existing = db.style_prompts.find_one({"prompt_type": "style_founder_content"})
    if existing:
        print("✅ Founder content template already exists, skipping...")
        return
    
    # Add new template
    new_template = {
        "platform": "xiaohongshu",
        "prompt_type": "style_founder_content",
        "name": "📱 Founder Social Media",
        "description": "Professional template for founders and entrepreneurs. Emphasizes insights and authenticity over marketing speak. Suitable for LinkedIn, Twitter, and XHS platforms."
    }
    
    result = db.style_prompts.insert_one(new_template)
    print(f"✅ Successfully added founder content template")
    print(f"   ID: {result.inserted_id}")
    print(f"   Type: style_founder_content")
    
    # List all templates
    prompts = list(db.style_prompts.find({}, {"_id": 0}))
    print(f"\n📊 Total templates in database: {len(prompts)}")
    for p in prompts:
        print(f"   • {p.get('name')} ({p.get('prompt_type')})")

if __name__ == "__main__":
    add_founder_template()
