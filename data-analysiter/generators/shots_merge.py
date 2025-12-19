import json
import os

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "raw")
DATA_DIR = os.path.join(BASE_DIR, "data")

PICTURES_JSON = os.path.join(RAW_DIR, "pictures.json")         # 你生成的图片镜头
SEGMENTS_JSON = os.path.join(RAW_DIR, "whisper_segments.json")         # whisper 输出
OUTPUT_JSON = os.path.join(DATA_DIR, "shots_merged.json")       # 最终镜头结构

def overlap(a1, a2, b1, b2):
    """计算两个时间区间的重合秒数"""
    return max(0, min(a2, b2) - max(a1, b1))


def main():
    # 读取图片信息
    with open(PICTURES_JSON, "r", encoding="utf-8") as f:
        pictures = json.load(f)

    # 读取 whisper 文本 segments
    with open(SEGMENTS_JSON, "r", encoding="utf-8") as f:
        segments = json.load(f)["segments"]

    # 给每个镜头加一个 text 字段
    for shot in pictures:
        shot["text"] = ""
        shot["segments"] = []

    # 开始对齐
    for seg in segments:
        s_start = seg["start"]
        s_end = seg["end"]

        best_shot = None
        best_overlap = 0

        # 遍历所有镜头，找重叠最多的
        for shot in pictures:
            p_start = shot["start"]
            p_end = shot["end"]

            ov = overlap(s_start, s_end, p_start, p_end)
            if ov > best_overlap:
                best_overlap = ov
                best_shot = shot

        if best_shot:
            best_shot["segments"].append(seg)
            best_shot["text"] += seg["text"]

    # 输出最终 JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(pictures, f, ensure_ascii=False, indent=2)

    print(f"🎉 镜头结构生成完成 → {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
