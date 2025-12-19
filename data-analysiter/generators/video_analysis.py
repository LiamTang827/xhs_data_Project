"""
将shots_merged.json转换为前端VideoAnalysisData格式
"""
import json
import os
import base64
from typing import List, Dict, Any

def time_to_string(seconds: float) -> str:
    """将秒数转换为 mm:ss 格式"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"

def get_image_base64(image_path: str) -> str:
    """将图片转换为base64编码（可选）"""
    try:
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                image_data = f.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')
                # 判断图片格式
                ext = os.path.splitext(image_path)[1].lower()
                mime_type = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
                return f"data:{mime_type};base64,{base64_data}"
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
    return ""

def determine_segment_id(start_time: float, total_duration: float) -> int:
    """根据时间判断镜头属于哪个段落
    1: 开头引言 (0-15%)
    2: 核心讲解 (15%-60%)
    3: 案例分析 (60%-90%)
    4: 结尾总结 (90%-100%)
    """
    percentage = start_time / total_duration
    if percentage < 0.15:
        return 1
    elif percentage < 0.60:
        return 2
    elif percentage < 0.90:
        return 3
    else:
        return 4

def transform_shots_to_frontend(
    input_file: str, 
    output_file: str,
    use_base64: bool = False,
    image_base_url: str = ""
) -> Dict[str, Any]:
    """
    转换shots_merged.json为前端格式
    
    参数:
        input_file: 输入的JSON文件路径
        output_file: 输出的JSON文件路径
        use_base64: 是否使用base64编码图片
        image_base_url: 图片的基础URL（如果不使用base64）
    """
    # 读取原始数据
    with open(input_file, 'r', encoding='utf-8') as f:
        shots_data = json.load(f)
    
    if not shots_data:
        print("No data found in input file")
        return {}
    
    # 计算总时长
    total_duration = max(shot['end'] for shot in shots_data)
    
    # 转换镜头数据
    transformed_shots = []
    for shot in shots_data:
        shot_id = shot['id']
        start = shot['start']
        end = shot['end']
        
        # 确定段落ID
        segment_id = determine_segment_id(start, total_duration)
        
        # 处理图片
        if use_base64 and shot.get('path'):
            image_url = get_image_base64(shot['path'])
        elif image_base_url:
            image_url = f"{image_base_url}/{shot['image']}"
        else:
            # 使用相对路径
            image_url = f"/images/shots/{shot['image']}"
        
        # 生成标题和副标题（基于文本内容）
        text = shot['text']
        if len(text) > 15:
            title = text[:12] + "..."
            subtitle = f"({text[12:20]}...)" if len(text) > 20 else f"({text[12:]})"
        else:
            title = text
            subtitle = f"(镜头{shot_id})"
        
        transformed_shot = {
            "id": shot_id,
            "title": title,
            "subtitle": subtitle,
            "image": image_url,
            "narration": text,
            "timeRange": f"{time_to_string(start)}-{time_to_string(end)}",
            "segmentId": segment_id
        }
        transformed_shots.append(transformed_shot)
    
    # 创建视频结构段落
    structure_segments = [
        {
            "id": 1,
            "label": "开头引言",
            "timeRange": f"(0:00-{time_to_string(total_duration * 0.15)})",
            "color": "blue",
            "width": "15%"
        },
        {
            "id": 2,
            "label": "核心讲解",
            "timeRange": f"({time_to_string(total_duration * 0.15)}-{time_to_string(total_duration * 0.60)})",
            "color": "green",
            "width": "45%"
        },
        {
            "id": 3,
            "label": "案例分析",
            "timeRange": f"({time_to_string(total_duration * 0.60)}-{time_to_string(total_duration * 0.90)})",
            "color": "purple",
            "width": "30%"
        },
        {
            "id": 4,
            "label": "结尾总结",
            "timeRange": f"({time_to_string(total_duration * 0.90)}-{time_to_string(total_duration)})",
            "color": "orange",
            "width": "10%"
        }
    ]
    
    # 生成时间标签
    time_labels = []
    num_labels = 6
    for i in range(num_labels):
        time_point = (total_duration / (num_labels - 1)) * i
        time_labels.append(time_to_string(time_point))
    
    # 构建最终数据
    frontend_data = {
        "shots": transformed_shots,
        "structureSegments": structure_segments,
        "totalDuration": time_to_string(total_duration),
        "timeLabels": time_labels
    }
    
    # 保存到文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(frontend_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 转换完成！")
    print(f"   总镜头数: {len(transformed_shots)}")
    print(f"   视频总时长: {time_to_string(total_duration)}")
    print(f"   输出文件: {output_file}")
    
    return frontend_data

if __name__ == "__main__":
    import os
    
    # 获取项目根目录
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    RAW_DIR = os.path.join(BASE_DIR, "raw")
    
    INPUT_FILE = os.path.join(DATA_DIR, "shots_merged.json")
    OUTPUT_FILE = os.path.join(DATA_DIR, "shots_frontend.json")
    
    # 如果shots_merged.json不存在，从raw目录复制
    if not os.path.exists(INPUT_FILE):
        raw_input = os.path.join(RAW_DIR, "shots_merged.json")
        if os.path.exists(raw_input):
            import shutil
            shutil.copy(raw_input, INPUT_FILE)
    
    # 选项2: 使用图片URL（推荐）
    transform_shots_to_frontend(
        INPUT_FILE, 
        OUTPUT_FILE, 
        use_base64=False,
        image_base_url="/api/images"  # 这个URL需要在后端配置
    )
    
    # 打印预览
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"\n📊 数据预览:")
        print(f"   前3个镜头:")
        for shot in data['shots'][:3]:
            print(f"   - 镜头{shot['id']}: {shot['title']} ({shot['timeRange']})")
