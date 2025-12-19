import whisper
import os
import warnings
import json

warnings.filterwarnings("ignore")

# ================= 配置 =================
VIDEO_FILE = "/Users/tangliam/Downloads/video.mp4"
MODEL_SIZE = "medium"  # 推荐 medium，tiny 太差
# ======================================

def main():
    if not os.path.exists(VIDEO_FILE):
        print(f"❌ 找不到文件: {VIDEO_FILE}")
        return

    print(f"🚀 正在加载 Whisper 模型 ({MODEL_SIZE})...")
    model = whisper.load_model(MODEL_SIZE)

    print("🎥 正在识别视频（将包含时间戳）...")

    # ☑ 关键修改：不要只拿 text，要拿 segments
    result = model.transcribe(
        VIDEO_FILE,
        fp16=False,
        language='Chinese',
        task="transcribe",   # 确保是语音识别而不是翻译
        verbose=True,        # 输出详细信息（包括 segments）
        temperature=0        # 减少随机性
    )

    # =============================
    # 1. 输出纯文本（你原来做的）
    # =============================
    print("\n================ 整篇文本 ================\n")
    print(result["text"])

    # =============================
    # 2. 输出带 start/end 的 segments（你真正需要的）
    # =============================
    segments = result.get("segments", [])
    print("\n================ 带时间戳的段落 ================\n")
    for seg in segments:
        print(f"[{seg['start']:.2f}s - {seg['end']:.2f}s] {seg['text']}")

    # =============================
    # 3. 保存 JSON 文件：后面结构化镜头就靠它了
    # =============================
    output_json = "whisper_segments.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n💾 已保存时间戳 JSON：{output_json}")

    # =============================
    # 4. 只保存 segments 文本（纯文字）
    # =============================
    output_txt = "whisper_text.txt"
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(result["text"])
    print(f"💾 已保存纯文本：{output_txt}")

if __name__ == "__main__":
    main()
