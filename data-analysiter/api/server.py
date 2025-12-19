"""
FastAPI服务 - 提供视频分析数据和图片
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import json
import os
from pathlib import Path
from typing import Optional

# MongoDB
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI(title="视频分析API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置路径
BASE_DIR = Path(__file__).parent.parent  # data-analysiter根目录
DATA_DIR = BASE_DIR / "data"
SHOTS_DATA_FILE = DATA_DIR / "shots_frontend.json"
CREATORS_DATA_FILE = DATA_DIR / "creators_data.json"
IMAGES_DIR = Path("/Users/tangliam/Downloads")

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "小红书数据分析API服务",
        "endpoints": {
            "video_analysis": "/api/video-analysis",
            "creators": "/api/creators",
            "images": "/api/images/{filename}",
            "health": "/api/health"
        }
    }

@app.get("/api/video-analysis")
async def get_video_analysis(note_id: Optional[str] = Query(None, description="可选的 note_id，用于将笔记信息注入到返回数据中")):
    """获取视频分析数据"""
    try:
        if not SHOTS_DATA_FILE.exists():
            raise HTTPException(
                status_code=404,
                detail=f"数据文件不存在: {SHOTS_DATA_FILE}. 请先运行 python -m generators.video_analysis"
            )
        
        with open(SHOTS_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 如果传入 note_id，尝试从 MongoDB 拉取笔记并注入数据
        if note_id:
            try:
                mongo_uri = os.environ.get('MONGODB_URI') or "mongodb+srv://xhs_user:S8VVePhiUHfT6H5U@xhs-cluster.omeyngi.mongodb.net/?retryWrites=true&w=majority&appName=xhs-Cluster"
                client = MongoClient(mongo_uri)
                db = client.get_database('media_crawler')
                notes_coll = db.get_collection('xhs_notes')

                note = notes_coll.find_one({'note_id': note_id})
                if not note:
                    # 尝试以 ObjectId 查询（如果前端传了 _id）
                    try:
                        note = notes_coll.find_one({'_id': ObjectId(note_id)})
                    except Exception:
                        note = None

                if note:
                    # 提取封面图片：优先使用 image_list，其次 cover
                    cover_url = ''
                    image_list = note.get('image_list')
                    if image_list:
                        if isinstance(image_list, list) and len(image_list) > 0:
                            cover_url = image_list[0].get('url', '') if isinstance(image_list[0], dict) else str(image_list[0])
                        elif isinstance(image_list, str):
                            cover_url = image_list
                    if not cover_url:
                        cover = note.get('cover')
                        if isinstance(cover, dict):
                            cover_url = cover.get('url', '')
                        elif isinstance(cover, str):
                            cover_url = cover
                    
                    # 只保留前端需要的字段，避免泄露敏感信息
                    filtered = {
                        'note_id': note.get('note_id') or str(note.get('_id')),
                        'title': note.get('title', ''),
                        'desc': note.get('desc', ''),
                        'video_url': note.get('video_url', ''),
                        'cover': cover_url,
                        'note_url': note.get('note_url', ''),
                        'liked_count': int(note.get('liked_count') or 0),
                        'collected_count': int(note.get('collected_count') or 0),
                        'comment_count': int(note.get('comment_count') or 0),
                        'share_count': int(note.get('share_count') or 0),
                        'user_id': note.get('user_id', ''),
                        'create_time': str(note.get('create_time', ''))
                    }
                    data['note'] = filtered

                client.close()
            except Exception as e:
                # 不阻塞主数据返回，记录错误到返回体里以便调试
                data.setdefault('_meta', {})['note_fetch_error'] = str(e)

        return JSONResponse(content=data)
    
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"JSON解析错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

@app.get("/api/images/{filename:path}")
async def get_image(filename: str):
    """获取镜头关键帧图片"""
    try:
        # 规范化并容错处理文件名
        raw = filename or ""
        # 去掉可能的不可见字符和两端空白
        candidate = raw.strip().replace('%20', ' ')

        # 列出目录文件并尝试多种匹配策略（精确、大小写不敏感、去除空格匹配）
        image_path = None
        if IMAGES_DIR.exists():
            files = [f for f in IMAGES_DIR.iterdir() if f.is_file()]
            # 精确匹配
            for f in files:
                if f.name == candidate:
                    image_path = f
                    break
            # URL编码形式匹配
            if not image_path:
                for f in files:
                    if f.name == candidate.replace(' ', '%20') or f.name.replace(' ', '%20') == candidate:
                        image_path = f
                        break
            # 大小写不敏感匹配
            if not image_path:
                lc = candidate.lower()
                for f in files:
                    if f.name.lower() == lc:
                        image_path = f
                        break
            # 宽松匹配：去掉空格/下划线/小数点后缀差异
            if not image_path:
                norm = ''.join(candidate.lower().split())
                for f in files:
                    if ''.join(f.name.lower().split()) == norm:
                        image_path = f
                        break
        
        if not image_path:
            # 列出目录中的所有文件以便调试
            if IMAGES_DIR.exists():
                available_files = [f.name for f in IMAGES_DIR.iterdir() if f.is_file()]
                raise HTTPException(
                    status_code=404,
                    detail=(f"图片不存在: {filename}\n" \
                            f"尝试匹配到的候选: {candidate}\n" \
                            f"可用文件（前50）: {available_files[:50]}")
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"图片目录不存在: {IMAGES_DIR}"
                )
        
        # 根据文件扩展名确定MIME类型
        ext = image_path.suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        media_type = mime_types.get(ext, 'image/jpeg')
        
        return FileResponse(
            path=str(image_path),
            media_type=media_type,
            headers={
                "Cache-Control": "public, max-age=86400",  # 缓存1天
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取图片失败: {str(e)}")

@app.get("/api/health")
async def health_check():
    """健康检查"""
    shots_data_exists = SHOTS_DATA_FILE.exists()
    creators_data_exists = CREATORS_DATA_FILE.exists()
    images_dir_exists = IMAGES_DIR.exists()
    
    # 统计图片数量
    image_count = 0
    if images_dir_exists:
        image_count = len([f for f in IMAGES_DIR.iterdir() if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']])
    
    return {
        "status": "ok",
        "video_analysis": {
            "exists": shots_data_exists,
            "path": str(SHOTS_DATA_FILE)
        },
        "creators_data": {
            "exists": creators_data_exists,
            "path": str(CREATORS_DATA_FILE)
        },
        "images_dir": {
            "exists": images_dir_exists,
            "path": str(IMAGES_DIR),
            "image_count": image_count
        }
    }

@app.get("/api/creators")
async def get_creators():
    """获取创作者网络数据"""
    try:
        if not CREATORS_DATA_FILE.exists():
            raise HTTPException(
                status_code=404,
                detail=f"创作者数据文件不存在: {CREATORS_DATA_FILE}. 请先运行 python -m generators.creators"
            )
        
        with open(CREATORS_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return JSONResponse(content=data)
    
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"JSON解析错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

@app.get("/api/images")
async def list_images():
    """列出所有可用的图片"""
    try:
        if not IMAGES_DIR.exists():
            raise HTTPException(status_code=404, detail=f"图片目录不存在: {IMAGES_DIR}")
        
        images = []
        for file in IMAGES_DIR.iterdir():
            if file.is_file() and file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                images.append({
                    "filename": file.name,
                    "size": file.stat().st_size,
                    "url": f"/api/images/{file.name}"
                })
        
        return {
            "total": len(images),
            "images": images[:50]  # 只返回前50个
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"列出图片失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 启动FastAPI小红书数据分析服务...")
    print(f"📁 视频分析数据: {SHOTS_DATA_FILE}")
    print(f"👥 创作者数据: {CREATORS_DATA_FILE}")
    print(f"🖼️  图片目录: {IMAGES_DIR}")
    print(f"🌐 服务地址: http://localhost:5001")
    print(f"\n📚 API文档:")
    print(f"  - Swagger UI: http://localhost:5001/docs")
    print(f"  - ReDoc: http://localhost:5001/redoc")
    print(f"\n可用端点:")
    print(f"  - GET /api/video-analysis - 获取视频分析数据")
    print(f"  - GET /api/creators - 获取创作者网络数据")
    print(f"  - GET /api/images/<filename> - 获取镜头图片")
    print(f"  - GET /api/images - 列出所有图片")
    print(f"  - GET /api/health - 健康检查")
    print()
    
    uvicorn.run(
        "api.server:app",  # 更新导入路径
        host="0.0.0.0",
        port=5001,
        reload=True,  # 开发模式自动重载
        log_level="info"
    )
