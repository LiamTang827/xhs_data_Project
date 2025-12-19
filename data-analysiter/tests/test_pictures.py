import os
import json

# ============================
# 配置区（按你的需求修改）
# ============================

# 图片所在的文件夹路径（你改成你的 Download 里图片所在的目录）
IMAGE_DIR = "/Users/tangliam/Downloads"

# 每张图片默认持续时间（单位：秒）
DEFAULT_DURATION = 6.0

# 输出 JSON 文件名
OUTPUT_JSON = "pictures.json"

# ============================
# 生成逻辑
# ============================

def main():
    # 1. 从目录中读取所有图片文件
    images = sorted([
        f for f in os.listdir(IMAGE_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ])

    if not images:
        print("❌ 目录中没有找到图片文件。")
        return

    print(f"📸 找到 {len(images)} 张图片，即将生成时间轴...")

    # 2. 按顺序生成 start / end 时间
    shots = []
    current_time = 0.0

    for idx, img in enumerate(images, start=1):
        start = current_time
        end = start + DEFAULT_DURATION
        current_time = end

        shots.append({
            "id": idx,
            "image": img,
            "path": os.path.join(IMAGE_DIR, img),  # 本地路径
            "start": round(start, 3),
            "end": round(end, 3)
        })

    # 3. 输出 JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(shots, f, ensure_ascii=False, indent=2)

    print(f"🎉 已生成 {OUTPUT_JSON}")
    print("✅ 完成！每张图片都带上了开始和结束时间。")

if __name__ == "__main__":
    main()
