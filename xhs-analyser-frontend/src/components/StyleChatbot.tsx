"use client";

import { useState, useEffect } from "react";

interface Creator {
  name: string;
  topics: string[];
  style: string;
  user_id: string;
  platform: string;
}

interface GenerateResult {
  success: boolean;
  content: string;
  error?: string;
}

export function StyleChatbot() {
  const [creators, setCreators] = useState<Creator[]>([]);
  const [selectedCreator, setSelectedCreator] = useState<string>("");
  const [userInput, setUserInput] = useState<string>("");
  const [generatedContent, setGeneratedContent] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  // 加载可用创作者列表
  const loadCreators = async () => {
    try {
      // 使用环境变量，默认localhost:8000（与后端端口一致）
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      console.log('🔍 [StyleChatbot] Loading creators from:', API_URL);
      
      const response = await fetch(`${API_URL}/api/style/creators`);
      console.log('📡 [StyleChatbot] Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      console.log('📦 [StyleChatbot] Received data:', data);
      
      if (data.success && data.creators && data.creators.length > 0) {
        setCreators(data.creators);
        console.log(`✅ [StyleChatbot] Loaded ${data.creators.length} creators`);
        
        // 默认选择硅谷樱花小姐姐
        const defaultCreator = data.creators.find((c: Creator) => 
          c.name === "硅谷樱花小姐姐🌸"
        );
        if (defaultCreator) {
          setSelectedCreator(defaultCreator.name);
        }
      } else {
        console.warn('⚠️  [StyleChatbot] No creators in response');
        setError("后端返回了空的创作者列表");
      }
    } catch (err) {
      console.error("❌ [StyleChatbot] 加载创作者列表失败:", err);
      setError(`无法加载创作者列表: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  useEffect(() => {
    loadCreators();
  }, []);

  const handleGenerate = async () => {
    if (!selectedCreator || !userInput.trim()) {
      setError("请选择创作者并输入内容描述");
      return;
    }

    setLoading(true);
    setError("");
    setGeneratedContent("");

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const selectedCreatorData = creators.find(c => c.name === selectedCreator);
      
      const response = await fetch(`${API_URL}/api/style/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          creator_name: selectedCreator,
          user_input: userInput,
          platform: selectedCreatorData?.platform || 'xiaohongshu',
        }),
      });

      const data: GenerateResult = await response.json();

      if (data.success && data.content) {
        setGeneratedContent(data.content);
      } else {
        setError(data.error || "生成失败");
      }
    } catch (err) {
      console.error("生成内容失败:", err);
      setError("生成失败，请检查API服务是否启动");
    } finally {
      setLoading(false);
    }
  };

  const selectedCreatorInfo = creators.find(c => c.name === selectedCreator);

  return (
    <div className="space-y-6">
      {/* 头部 */}
      <div className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm">
        <h2 className="text-2xl font-semibold text-black mb-2">
          ✍️ AI风格模仿生成器
        </h2>
        <p className="text-sm text-black/60">
          选择创作者 → 输入内容 → 一键生成爆款文案
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* 左侧：输入区 */}
        <div className="space-y-4">
          {/* 创作者选择 */}
          <div className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm">
            <label className="block text-sm font-semibold text-black mb-3">
              选择要模仿的创作者
            </label>
            <select
              value={selectedCreator}
              onChange={(e) => setSelectedCreator(e.target.value)}
              className="w-full rounded-lg border border-black/20 bg-white px-4 py-3 text-black focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            >
              <option value="">-- 请选择 --</option>
              {creators.map((creator) => (
                <option key={creator.name} value={creator.name}>
                  {creator.name}
                </option>
              ))}
            </select>
          </div>

          {/* 内容输入区 */}
          <div className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm">
            <label className="block text-sm font-semibold text-black mb-3">
              你想创作什么内容？
            </label>
            <textarea
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="例如：介绍一下最新的AI工具...&#10;&#10;💡 提示：可以从左侧星图的「流量密码」复制热点话题，粘贴到这里，让AI融入这些热门标签！"
              rows={8}
              className="w-full rounded-lg border border-black/20 bg-white px-4 py-3 text-black placeholder:text-black/40 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 resize-none"
            />
          </div>

          {/* 热点话题展示区（只读，提示复制） */}
          {selectedCreatorInfo && selectedCreatorInfo.topics.length > 0 && (
            <div className="rounded-2xl border border-purple-200 bg-gradient-to-br from-purple-50 to-pink-50 p-6 shadow-sm">
              <div className="flex items-center gap-2 mb-3">
                <h4 className="text-sm font-semibold text-black">
                  🔥 TA的热点话题
                </h4>
                <span className="text-xs text-black/40">·</span>
                <span className="text-xs text-black/60">基于最近30天爆款笔记</span>
              </div>
              <p className="text-xs text-purple-700 mb-3">
                💡 点击话题复制，然后粘贴到上方内容框，AI会自动融入这些热点！
              </p>
              <div className="flex flex-wrap gap-2">
                {selectedCreatorInfo.topics.map((topic, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      navigator.clipboard.writeText(`#${topic}`);
                      // 简单的视觉反馈
                      const btn = document.getElementById(`topic-btn-${idx}`);
                      if (btn) {
                        btn.textContent = '✓ 已复制';
                        setTimeout(() => {
                          btn.textContent = `#${topic}`;
                        }, 1000);
                      }
                    }}
                    id={`topic-btn-${idx}`}
                    className="group rounded-lg px-3 py-2 text-sm font-medium bg-white text-purple-700 border-2 border-purple-300 hover:border-purple-600 hover:bg-purple-50 transition-all hover:scale-105 active:scale-95 cursor-pointer"
                    title="点击复制话题"
                  >
                    #{topic}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* 生成按钮 */}
          <div className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm">
            <button
              onClick={handleGenerate}
              disabled={loading || !selectedCreator || !userInput.trim()}
              className="w-full rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4 text-white font-semibold hover:from-blue-700 hover:to-purple-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
            >
              {loading ? "🎨 AI创作中..." : "🚀 一键生成爆款文案"}
            </button>

            {error && (
              <div className="mt-3 rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-600">
                ❌ {error}
              </div>
            )}
          </div>
        </div>

        {/* 右侧：生成结果 */}
        <div className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-black mb-4">
            📝 生成的文案
          </h3>
          
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
                <p className="mt-3 text-sm text-black/60">AI正在创作中...</p>
              </div>
            </div>
          )}

          {!loading && !generatedContent && (
            <div className="flex items-center justify-center py-12 text-black/40">
              <div className="text-center">
                <div className="text-4xl mb-2">✨</div>
                <p className="text-sm">生成的文案将显示在这里</p>
              </div>
            </div>
          )}

          {!loading && generatedContent && (
            <div className="space-y-4">
              <div className="rounded-lg bg-gradient-to-br from-blue-50 to-purple-50 p-6">
                <pre className="whitespace-pre-wrap font-sans text-sm text-black/80 leading-relaxed">
                  {generatedContent}
                </pre>
              </div>
              
              <button
                onClick={() => {
                  navigator.clipboard.writeText(generatedContent);
                  alert("文案已复制到剪贴板！");
                }}
                className="w-full rounded-lg border-2 border-blue-600 bg-white px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 transition-colors"
              >
                📋 复制文案
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
