"use client";

import { useState, useEffect } from "react";

interface Creator {
  nickname: string;
  user_id: string;
  topics: string[];
}

interface ContentOpportunity {
  note_title: string;
  note_id?: string;
  engagement_index: number;
  engagement_count: number;
  reason: string;
  direction: string; // note desc / body text
  angles: string[];
}

interface PromptTemplate {
  prompt_type: string;
  name: string;
  description: string;
}

interface Props {
  myCreator: Creator;
  selectedContent: ContentOpportunity;
  onContentGenerated: (content: string) => void;
  onBack: () => void;
  onReset: () => void;
}

export default function StepGenerateContent({
  myCreator,
  selectedContent,
  onContentGenerated,
  onBack,
  onReset
}: Props) {
  const [templates, setTemplates] = useState<PromptTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>("");
  const [userGuidance, setUserGuidance] = useState<string>("");
  const [generatedContent, setGeneratedContent] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showResult, setShowResult] = useState(false);
  const [copiedGenerated, setCopiedGenerated] = useState(false);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
      const response = await fetch(`${API_URL}/api/style/prompts?platform=xiaohongshu`);

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      if (data.success && data.prompts) {
        setTemplates(data.prompts);
        if (data.prompts.length > 0) {
          setSelectedTemplate(data.prompts[0].prompt_type);
        }
      }
    } catch (err) {
      console.error("加载模板失败:", err);
    }
  };

  const handleCopyGenerated = async () => {
    try {
      await navigator.clipboard.writeText(generatedContent);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = generatedContent;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
    }
    setCopiedGenerated(true);
    setTimeout(() => setCopiedGenerated(false), 2000);
  };

  const handleGenerate = async () => {
    if (!selectedTemplate) {
      setError("请选择一个模板");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

      // Build prompt: real note content + user's own guidance
      const noteBody = selectedContent.direction || "";
      const prompt = [
        "基于以下参考笔记，生成一篇属于我风格的全新创作文案。",
        "",
        "【参考笔记】",
        `标题：${selectedContent.note_title}`,
        noteBody ? `正文：${noteBody}` : "",
        "",
        "【我的账号信息】",
        `创作者：${myCreator.nickname}`,
        myCreator.topics.length > 0 ? `内容方向：${myCreator.topics.join("、")}` : "",
        "",
        userGuidance ? `【我的额外要求】\n${userGuidance}` : "",
        "",
        "要求：",
        "1. 不要照搬原文，要结合我的风格重新创作",
        "2. 保留参考笔记中值得借鉴的结构和亮点",
        "3. 生成标题 + 正文，适合小红书发布",
      ].filter(Boolean).join("\n");

      const response = await fetch(`${API_URL}/api/style/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          creator_name: myCreator.nickname,
          prompt_type: selectedTemplate,
          user_input: prompt
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();
      if (data.success && data.content) {
        setGeneratedContent(data.content);
        onContentGenerated(data.content);
        setShowResult(true);
      } else {
        setError("生成文案失败");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "生成文案失败");
    } finally {
      setLoading(false);
    }
  };

  if (showResult) {
    return (
      <div className="space-y-6">
        {/* 成功提示 */}
        <div className="rounded-2xl bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 p-6">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🎉</span>
            <div>
              <h2 className="text-xl font-bold text-gray-900">文案生成完成！</h2>
              <p className="text-gray-600 text-sm">你可以复制文案或重新调整后再次生成</p>
            </div>
          </div>
        </div>

        {/* 生成文案显示 */}
        <div className="rounded-2xl bg-white border border-black/10 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-semibold text-gray-900">📝 生成的文案</h3>
            <div className="flex gap-2">
              <button
                onClick={handleCopyGenerated}
                className={`rounded-lg px-4 py-2 text-sm font-medium transition-all ${
                  copiedGenerated
                    ? "bg-green-100 text-green-700"
                    : "bg-blue-600 text-white hover:bg-blue-700"
                }`}
              >
                {copiedGenerated ? "✓ 已复制" : "📋 复制文案"}
              </button>
              <button
                onClick={() => setShowResult(false)}
                className="rounded-lg border border-purple-300 text-purple-600 px-4 py-2 text-sm font-medium hover:bg-purple-50 transition-colors"
              >
                ✏️ 重新调整
              </button>
            </div>
          </div>
          <div className="bg-gray-50 rounded-xl p-5 max-h-[480px] overflow-y-auto">
            <p className="text-gray-900 whitespace-pre-wrap leading-relaxed text-sm">
              {generatedContent}
            </p>
          </div>
        </div>

        {/* 生成信息 */}
        <div className="rounded-2xl bg-gray-50 border border-gray-200 p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">📊 生成信息</h3>
          <div className="grid grid-cols-3 gap-3 text-xs">
            <div className="bg-white rounded-lg p-3 border border-gray-100">
              <div className="text-gray-400 mb-0.5">参考笔记</div>
              <div className="font-medium text-gray-900 line-clamp-1">{selectedContent.note_title}</div>
            </div>
            <div className="bg-white rounded-lg p-3 border border-gray-100">
              <div className="text-gray-400 mb-0.5">选用模板</div>
              <div className="font-medium text-gray-900">
                {templates.find(t => t.prompt_type === selectedTemplate)?.name || selectedTemplate}
              </div>
            </div>
            <div className="bg-white rounded-lg p-3 border border-gray-100">
              <div className="text-gray-400 mb-0.5">创作者</div>
              <div className="font-medium text-gray-900">{myCreator.nickname}</div>
            </div>
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="flex gap-4">
          <button
            onClick={onBack}
            className="rounded-lg border border-black/20 px-6 py-3.5 text-gray-700 font-semibold hover:bg-gray-50 transition-colors"
          >
            ← 返回上一步
          </button>
          <button
            onClick={onReset}
            className="rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3.5 font-semibold hover:from-purple-700 hover:to-pink-700 transition-colors"
          >
            🔄 开始新的创作
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-2xl bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <span>✨</span> 第三步：生成创作文案
        </h2>
        <p className="text-black/60 mt-1">
          参考笔记内容已就绪，选择模板并添加你的要求，一键生成文案
        </p>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700 font-medium">
          ⚠️ {error}
        </div>
      )}

      {/* Main 2-column layout */}
      <div className="flex gap-5 items-start">
        {/* Left: reference note + guidance */}
        <div className="flex-1 min-w-0 space-y-4">
          {/* Reference note card */}
          <div className="rounded-2xl bg-white border border-black/5 shadow-sm p-5 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-1.5">
                <span>📄</span> 参考笔记
              </h3>
              {selectedContent.engagement_count > 0 && (
                <span className="text-xs text-orange-500 font-medium bg-orange-50 px-2 py-0.5 rounded-full">
                  🔥 {selectedContent.engagement_count.toLocaleString()} 互动
                </span>
              )}
            </div>

            <div className="bg-gray-50 rounded-xl p-4">
              <h4 className="font-semibold text-gray-900 text-sm mb-2">
                {selectedContent.note_title}
              </h4>
              {selectedContent.direction && (
                <p className="text-xs text-gray-600 leading-relaxed whitespace-pre-wrap max-h-48 overflow-y-auto">
                  {selectedContent.direction}
                </p>
              )}
            </div>

            {selectedContent.reason && (
              <p className="text-xs text-gray-400 px-1">💡 {selectedContent.reason}</p>
            )}
          </div>

          {/* User guidance */}
          <div className="rounded-2xl bg-white border border-black/5 shadow-sm p-5 space-y-3">
            <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-1.5">
              <span>✏️</span> 你的创作要求
              <span className="text-xs font-normal text-gray-400">（可选，自由发挥）</span>
            </h3>
            <textarea
              value={userGuidance}
              onChange={(e) => setUserGuidance(e.target.value)}
              placeholder={"可以写你想要的风格、语气、重点方向等，例如：\n• 用轻松口语化的方式写\n• 重点突出实用干货\n• 开头要有 hook 吸引读者\n• 加入个人经历故事"}
              className="w-full rounded-xl border border-gray-200 px-4 py-3 text-sm text-gray-900 placeholder:text-gray-400 focus:border-purple-400 focus:outline-none focus:ring-2 focus:ring-purple-400/20 resize-none"
              rows={5}
            />
          </div>
        </div>

        {/* Right: template selection + generate */}
        <div className="w-72 shrink-0 space-y-4">
          {/* Template picker */}
          <div className="rounded-2xl bg-white border border-black/5 shadow-sm overflow-hidden">
            <div className="p-4 border-b border-gray-100 bg-gray-50/50">
              <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-1.5">
                <span>🎨</span> 选择模板
              </h3>
            </div>
            <div className="p-2 space-y-1 max-h-[360px] overflow-y-auto">
              {templates.length === 0 ? (
                <div className="text-xs text-gray-400 text-center py-6">加载模板中...</div>
              ) : (
                templates.map((template) => (
                  <button
                    key={template.prompt_type}
                    onClick={() => setSelectedTemplate(template.prompt_type)}
                    className={`w-full text-left rounded-xl border p-3 transition-all ${
                      selectedTemplate === template.prompt_type
                        ? "border-purple-400 bg-purple-50 shadow ring-1 ring-purple-200"
                        : "border-transparent hover:border-purple-200 hover:bg-purple-50/40"
                    }`}
                  >
                    <div className="text-sm font-medium text-gray-900">{template.name}</div>
                    <div className="text-xs text-gray-500 mt-0.5 line-clamp-2">{template.description}</div>
                  </button>
                ))
              )}
            </div>
          </div>

          {/* Generate button */}
          <button
            onClick={handleGenerate}
            disabled={loading || !selectedTemplate}
            className={`w-full rounded-xl px-5 py-3.5 text-white font-semibold transition-all ${
              selectedTemplate && !loading
                ? "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 shadow-lg"
                : "bg-gray-300 cursor-not-allowed"
            }`}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-r-transparent" />
                生成中...
              </span>
            ) : (
              "✨ 生成文案"
            )}
          </button>

          {!selectedTemplate && templates.length > 0 && (
            <p className="text-xs text-gray-400 text-center">← 请先选择模板</p>
          )}
        </div>
      </div>

      {/* Back button */}
      <div className="pt-2">
        <button
          onClick={onBack}
          className="rounded-lg border border-black/20 px-6 py-3.5 text-gray-700 font-semibold hover:bg-gray-50 transition-colors"
        >
          ← 上一步
        </button>
      </div>
    </div>
  );
}
