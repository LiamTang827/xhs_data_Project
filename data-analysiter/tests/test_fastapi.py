"""
测试FastAPI服务 - 完整测试套件
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_list_images():
    """测试列出图片"""
    print("🖼️  测试列出图片...")
    response = requests.get(f"{BASE_URL}/api/images")
    data = response.json()
    print(f"状态码: {response.status_code}")
    print(f"图片总数: {data['total']}")
    print(f"前5个图片:")
    for img in data['images'][:5]:
        print(f"  - {img['filename']} ({img['size']} bytes)")
    print()

def test_get_image(filename):
    """测试获取单个图片"""
    print(f"📷 测试获取图片: {filename}")
    response = requests.get(f"{BASE_URL}/api/images/{filename}")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"文件大小: {len(response.content)} bytes")
        print("✅ 图片获取成功!")
    else:
        print(f"❌ 错误: {response.text}")
    print()

def test_video_analysis():
    """测试视频分析数据"""
    print("📊 测试视频分析数据...")
    response = requests.get(f"{BASE_URL}/api/video-analysis")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"镜头数量: {len(data['shots'])}")
        print(f"总时长: {data['totalDuration']}")
        print(f"前3个镜头:")
        for shot in data['shots'][:3]:
            print(f"  - 镜头{shot['id']}: {shot['title']} ({shot['timeRange']})")
    else:
        print(f"❌ 错误: {response.text}")
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("FastAPI服务测试")
    print("=" * 50)
    print()
    
    try:
        test_health()
        test_list_images()
        test_get_image("IMG_8779.JPG")
        test_get_image("IMG_8798.JPG")
        test_video_analysis()
        
        print("✅ 所有测试完成!")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保API服务已启动:")
        print("   python3 api_server_fastapi.py")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
