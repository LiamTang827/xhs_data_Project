"use client";

import { useState } from "react";

interface Creator {
  nickname: string;
  user_id: string;
  followers: number;
  total_engagement: number;
  topics: string[];
  avatar?: string;
}

interface ContentOpportunity {
  note_title: string;
  note_id: string;
  engagement_index: number;
  engagement_count: number;
  reason: string;
  direction: string;
  angles: string[];
}

interface NoteSearchResult {
  note_id: string;
  user_id: string;
  title: string;
  desc: string;
  similarity: number;
  likes: number;
  collected_count: number;
  comments_count: number;
  share_count: number;
  engagement_score: number;
  nickname: string;
  avatar: string;
  note_create_time: number;
}

interface Props {
  myCreator: Creator;
  similarCreators: Creator[];
  selectedCompetitor: Creator | null;
  contentOpportunities: ContentOpportunity[];
  minEngagement: number;
  topN: number;
  days: number | null;
  onCompetitorSelected: (competitor: Creator) => void;
  onContentDiscovered: (opportunities: ContentOpportunity[]) => void;
  onContentSelected: (content: ContentOpportunity) => void;
  onParameterChange: (params: any) => void;
  onBack: () => void;
}

export default function StepDiscoverContent({
  myCreator,
  similarCreators,
  selectedCompetitor,
  contentOpportunities,
  minEngagement,
  topN,
  days,
  onCompetitorSelected,
  onContentDiscovered,
  onContentSelected,
  onParameterChange,
  onBack
}: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Tab
  const [activeTab, setActiveTab] = useState<"analyze" | "search">("analyze");

  // 笔记搜索状态
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<NoteSearchResult[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [searchMeta, setSearchMeta] = useState<{
    total: number;
    search_time_ms: number;
    index_size: number;
  } | null>(null);

  const handleAnalyze = async () => {
    if (!selectedCompetitor) return;

    setLoading(true);
    setError("");

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
      const params = new URLSearchParams({
        top_n: String(topN),
        min_engagement: String(minEngagement),
      });
      if (days) params.set('days', String(days));
      const response = await fetch(
        `${API_URL}/api/creators/growth-path/${myCreator.user_id}/${selectedCompetitor.user_id}?${params}`
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();
      if (data.success && data.data) {
        onContentDiscovered(data.data.opportunities);
      } else {
        setError("发现爆品内容失败");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "分析失败");
    } finally {
      setLoading(false);
    }
  };

  // 笔记语义搜索
  const handleNoteSearch = async () => {
    if (!searchQuery.trim()) return;

    setSearchLoading(true);
    setSearchError("");
    setSearchResults([]);
    setSearchMeta(null);

    try {
      const res = await fetch("/api/notes/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery.trim(), top_k: 20 }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      if (data.success) {
        setSearchResults(data.results || []);
        setSearchMeta({
          total: data.total || 0,
          search_time_ms: data.search_time_ms || 0,
          index_size: data.index_size || 0,
        });
      } else {
        setSearchError(data.message || "搜索失败");
      }
    } catch (err) {
      setSearchError(err instanceof Error ? err.message : "搜索失败");
    } finally {
      setSearchLoading(false);
    }
  };

  // 将搜索结果转换为 ContentOpportunity 格式，方便传递到下一步
  const selectSearchResult = (note: NoteSearchResult) => {
    const opportunity: ContentOpportunity = {
      note_title: note.title || "(无标题)",
      note_id: note.note_id,
      engagement_index: note.engagement_score / 1000,
      engagement_count: note.likes + note.collected_count + note.comments_count,
      reason: `搜索匹配度 ${(note.similarity * 100).toFixed(0)}% — 来自 ${note.nickname || "未知创作者"}`,
      direction: note.desc ? note.desc.slice(0, 200) : "",
      angles: [],
    };
    onContentSelected(opportunity);
  };

  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 p-8">
        <h2 className="text-2xl font-bold text-black mb-2">🎬 第三步：发现爆品内容</h2>
        <p className="text-black/60">
          从相似博主的爆款内容中，找出最有可能适合你的创作方向，或搜索任意关键词找到相关笔记
        </p>
      </div>

      {/* Tab 切换 */}
      <div className="flex rounded-xl bg-gray-100 p-1">
        <button
          onClick={() => setActiveTab("analyze")}
          className={`flex-1 rounded-lg px-4 py-3 text-sm font-semibold transition-all ${
            activeTab === "analyze"
              ? "bg-white text-purple-700 shadow-sm"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          🎯 对标分析
        </button>
        <button
          onClick={() => setActiveTab("search")}
          className={`flex-1 rounded-lg px-4 py-3 text-sm font-semibold transition-all ${
            activeTab === "search"
              ? "bg-white text-purple-700 shadow-sm"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          🔍 笔记语义搜索
        </button>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-600">
          ❌ {error}
        </div>
      )}

      {/* ========== Tab: 对标分析 ========== */}
      {activeTab === "analyze" && (
        <div className="grid gap-6 lg:grid-cols-3">
          {/* 左侧：参数设置 */}
          <div className="lg:col-span-1 space-y-4">
            {/* 竞品选择 */}
            <div className="rounded-2xl bg-white border border-black/10 p-6 shadow-sm">
              <label className="block text-sm font-semibold text-black mb-3">
                 选择对标博主
              </label>
              <select
                value={selectedCompetitor?.user_id || ""}
                onChange={(e) => {
                  const creator = similarCreators.find(c => c.user_id === e.target.value);
                  if (creator) onCompetitorSelected(creator);
                }}
                className="w-full rounded-lg border border-black/20 bg-white px-4 py-3 text-black focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20"
              >
                <option value="">-- 请选择 --</option>
                {similarCreators.map((creator) => (
                  <option key={creator.user_id} value={creator.user_id}>
                    {creator.nickname}
                  </option>
                ))}
              </select>

              {selectedCompetitor && (
                <div className="mt-3 p-3 bg-purple-50 rounded-lg text-xs space-y-1">
                  <div className="flex justify-between">
                    <span className="text-black/60">粉丝:</span>
                    <span className="font-semibold">{selectedCompetitor.followers.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-black/60">互动:</span>
                    <span className="font-semibold">{selectedCompetitor.total_engagement.toLocaleString()}</span>
                  </div>
                </div>
              )}
            </div>

            {/* 分析参数 */}
            <div className="rounded-2xl bg-white border border-black/10 p-6 shadow-sm">
              <h3 className="text-sm font-semibold text-black mb-4">⚙️ 分析参数</h3>

              <div className="space-y-4">
                {/* 时间范围 */}
                <div>
                  <label className="block text-xs text-black/60 mb-2">
                    时间范围
                  </label>
                  <div className="flex rounded-lg bg-gray-100 p-0.5">
                    {[
                      { label: "近一周", value: 7 },
                      { label: "近一月", value: 30 },
                      { label: "全部", value: null },
                    ].map((opt) => (
                      <button
                        key={opt.label}
                        onClick={() => onParameterChange({ days: opt.value })}
                        className={`
                          flex-1 text-xs font-medium py-2 rounded-md transition-all
                          ${days === opt.value
                            ? "bg-white text-purple-700 shadow-sm"
                            : "text-gray-500 hover:text-gray-700"
                          }
                        `}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-xs text-black/60 mb-2">
                    最相关笔记数量: {topN}个
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={topN}
                    onChange={(e) => onParameterChange({ topN: Number(e.target.value) })}
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-xs text-black/60 mb-2">
                    爆款阈值: {minEngagement.toFixed(1)} ≈ {(minEngagement * 1000).toLocaleString()}互动
                  </label>
                  <input
                    type="range"
                    min="0.5"
                    max="5"
                    step="0.5"
                    value={minEngagement}
                    onChange={(e) => onParameterChange({ minEngagement: Number(e.target.value) })}
                    className="w-full"
                  />
                </div>
              </div>
            </div>

            {/* 分析按钮 */}
            <button
              onClick={handleAnalyze}
              disabled={loading || !selectedCompetitor}
              className={`
                w-full rounded-lg px-6 py-4 text-white font-semibold transition-all
                ${
                  selectedCompetitor && !loading
                    ? "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 shadow-lg"
                    : "bg-gray-300 cursor-not-allowed"
                }
              `}
            >
              {loading ? "🔍 分析中..." : "🔍 分析爆品"}
            </button>
          </div>

          {/* 右侧：结果展示 */}
          <div className="lg:col-span-2 space-y-4">
            {loading && (
              <div className="rounded-2xl bg-white border border-black/10 p-12 shadow-sm">
                <div className="flex flex-col items-center justify-center">
                  <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-purple-600 border-r-transparent"></div>
                  <p className="mt-4 text-sm text-black/60">AI正在深度分析中...</p>
                </div>
              </div>
            )}

            {!loading && contentOpportunities.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-gray-900 px-2 flex items-center gap-2">
                  <span>✨</span> 发现 {contentOpportunities.length} 个爆品机会
                </h3>

                {contentOpportunities.map((opp, idx) => (
                  <button
                    key={idx}
                    onClick={() => onContentSelected(opp)}
                    className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm hover:shadow-md hover:border-purple-300 transition-all text-left"
                  >
                    {/* 标题和数据 */}
                    <div className="flex items-start justify-between gap-4 mb-3">
                      <h4 className="text-base font-semibold text-black flex-1">
                        {idx + 1}. {opp.note_title}
                      </h4>
                      <div className="flex flex-col items-end gap-1">
                        <div className="flex items-center gap-1 text-xs">
                          <span className="text-black/60">互动指数</span>
                          <span className="font-semibold text-orange-600">
                            {opp.engagement_index.toFixed(2)}
                          </span>
                        </div>
                        <div className="text-xs text-black/40">
                          ≈{opp.engagement_count.toLocaleString()}互动
                        </div>
                      </div>
                    </div>

                    {/* 分析内容 */}
                    {opp.reason && (
                      <div className="mb-2 p-2 bg-amber-50 rounded text-xs">
                        <div className="font-semibold text-amber-900 mb-1">为什么值得借鉴</div>
                        <p className="text-amber-800/80">{opp.reason}</p>
                      </div>
                    )}

                    {opp.direction && (
                      <div className="mb-2 p-2 bg-blue-50 rounded text-xs">
                        <div className="font-semibold text-blue-900 mb-1">你可以这样做</div>
                        <p className="text-blue-800/80">{opp.direction}</p>
                      </div>
                    )}

                    {opp.angles && opp.angles.length > 0 && (
                      <div className="p-2 bg-green-50 rounded text-xs">
                        <div className="font-semibold text-green-900 mb-1">具体角度</div>
                        <ul className="space-y-1">
                          {opp.angles.map((angle, i) => (
                            <li key={i} className="text-green-800">
                              • {angle}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="mt-3 text-purple-600 text-sm font-semibold">
                      选择这个内容 →
                    </div>
                  </button>
                ))}
              </div>
            )}

            {!loading && contentOpportunities.length === 0 && selectedCompetitor && (
              <div className="rounded-2xl bg-white border border-black/10 p-12 shadow-sm">
                <div className="flex flex-col items-center justify-center text-black/40">
                  <div className="text-5xl mb-4">🎯</div>
                  <p className="text-sm">点击上方"分析爆品"按钮开始分析</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========== Tab: 笔记语义搜索 ========== */}
      {activeTab === "search" && (
        <div className="space-y-6">
          {/* 搜索框 */}
          <div className="rounded-2xl bg-white border border-black/10 p-6 shadow-sm">
            <h3 className="text-sm font-semibold text-black mb-3">
              🔍 输入关键词，语义搜索相关笔记
            </h3>
            <p className="text-xs text-gray-500 mb-4">
              系统将把你的搜索词转化为向量，与所有笔记内容进行语义相似度匹配
            </p>
            <div className="flex gap-3">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleNoteSearch()}
                placeholder="例如：AI教程、旅行攻略、美食推荐、职场干货..."
                className="flex-1 rounded-lg border border-gray-300 px-4 py-3 text-sm focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20"
              />
              <button
                onClick={handleNoteSearch}
                disabled={searchLoading || !searchQuery.trim()}
                className="rounded-lg bg-purple-600 px-6 py-3 text-sm font-semibold text-white hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
              >
                {searchLoading ? "搜索中..." : "语义搜索"}
              </button>
            </div>
          </div>

          {searchError && (
            <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-600">
              ⚠️ {searchError}
            </div>
          )}

          {/* 搜索元信息 */}
          {searchMeta && (
            <div className="flex items-center gap-4 text-xs text-gray-500 px-2">
              <span>找到 <strong className="text-purple-600">{searchMeta.total}</strong> 条结果</span>
              <span>•</span>
              <span>耗时 {searchMeta.search_time_ms}ms</span>
              <span>•</span>
              <span>索引 {searchMeta.index_size} 条笔记</span>
            </div>
          )}

          {/* 搜索中 */}
          {searchLoading && (
            <div className="rounded-2xl bg-white border border-black/10 p-12 shadow-sm">
              <div className="flex flex-col items-center justify-center">
                <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-purple-600 border-r-transparent" />
                <p className="mt-4 text-sm text-black/60">语义搜索中...</p>
              </div>
            </div>
          )}

          {/* 搜索结果列表 */}
          {!searchLoading && searchResults.length > 0 && (
            <div className="space-y-3">
              {searchResults.map((note, idx) => (
                <button
                  key={note.note_id}
                  onClick={() => selectSearchResult(note)}
                  className="w-full rounded-2xl border border-black/10 bg-white p-5 shadow-sm hover:shadow-md hover:border-purple-300 transition-all text-left"
                >
                  <div className="flex items-start gap-4">
                    {/* 排名 + 相似度 */}
                    <div className="flex flex-col items-center gap-1 min-w-[48px]">
                      <div className="text-lg font-bold text-gray-400">#{idx + 1}</div>
                      <div className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                        note.similarity >= 0.8
                          ? "bg-green-100 text-green-700"
                          : note.similarity >= 0.6
                            ? "bg-yellow-100 text-yellow-700"
                            : "bg-gray-100 text-gray-600"
                      }`}>
                        {(note.similarity * 100).toFixed(0)}%
                      </div>
                    </div>

                    <div className="flex-1 min-w-0">
                      {/* 标题 */}
                      <h4 className="text-base font-semibold text-black mb-1 line-clamp-2">
                        {note.title || "(无标题)"}
                      </h4>

                      {/* 创作者信息 */}
                      <div className="flex items-center gap-2 mb-2">
                        {note.avatar && (
                          <img
                            src={note.avatar}
                            alt={note.nickname}
                            className="w-5 h-5 rounded-full object-cover"
                          />
                        )}
                        <span className="text-xs text-gray-500">{note.nickname || "未知"}</span>
                      </div>

                      {/* 描述预览 */}
                      {note.desc && (
                        <p className="text-xs text-gray-600 line-clamp-2 mb-2">{note.desc}</p>
                      )}

                      {/* 互动指标 */}
                      <div className="flex flex-wrap gap-3 text-xs text-gray-500">
                        <span>👍 {note.likes.toLocaleString()}</span>
                        <span>💾 {note.collected_count.toLocaleString()}</span>
                        <span>💬 {note.comments_count.toLocaleString()}</span>
                        {note.share_count > 0 && <span>🔗 {note.share_count.toLocaleString()}</span>}
                      </div>
                    </div>

                    {/* 选择箭头 */}
                    <div className="text-purple-400 text-sm self-center">
                      选择 →
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* 空状态 */}
          {!searchLoading && searchResults.length === 0 && !searchMeta && (
            <div className="rounded-2xl bg-white border border-black/10 p-12 shadow-sm">
              <div className="flex flex-col items-center justify-center text-black/40">
                <div className="text-5xl mb-4">🔍</div>
                <p className="text-sm mb-2">输入关键词，在所有笔记中进行语义搜索</p>
                <p className="text-xs text-gray-400">
                  支持自然语言查询，如"如何用AI做内容"、"旅行Vlog拍摄技巧"
                </p>
              </div>
            </div>
          )}

          {/* 搜索无结果 */}
          {!searchLoading && searchResults.length === 0 && searchMeta && (
            <div className="rounded-2xl bg-white border border-black/10 p-12 shadow-sm">
              <div className="flex flex-col items-center justify-center text-black/40">
                <div className="text-5xl mb-4">📭</div>
                <p className="text-sm">未找到匹配的笔记</p>
                <p className="text-xs mt-1">
                  {searchMeta.index_size === 0
                    ? "暂无笔记 embedding 数据，请先运行 generate_note_embeddings.py"
                    : "试试换个关键词？"}
                </p>
              </div>
            </div>
          )}

          {/* 说明 */}
          <div className="rounded-lg bg-blue-50 border border-blue-200 p-4 text-sm text-blue-800">
            <div className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
              <span>💡</span> 语义搜索说明
            </div>
            <ul className="space-y-1 text-xs">
              <li>• 使用 BAAI/bge-small-zh-v1.5 模型将查询和笔记内容都转化为 512 维向量</li>
              <li>• 通过余弦相似度匹配，找到语义上最接近的笔记（不只是关键词匹配）</li>
              <li>• 相似度 <span className="text-green-700 font-medium">≥80%</span> 高度相关，<span className="text-yellow-700 font-medium">60-80%</span> 较相关</li>
              <li>• 点击搜索结果可以直接选择该笔记作为创作参考，进入下一步</li>
            </ul>
          </div>
        </div>
      )}

      {/* 操作按钮 */}
      <div className="flex gap-4">
        <button
          onClick={onBack}
          className="flex-1 rounded-lg border border-black/20 px-6 py-4 text-black font-semibold hover:bg-gray-50 transition-colors"
        >
          ← 上一步
        </button>
        <button
          onClick={() => {
            if (contentOpportunities.length > 0) {
              onContentSelected(contentOpportunities[0]);
            }
          }}
          disabled={contentOpportunities.length === 0}
          className={`
            flex-1 rounded-lg px-6 py-4 text-white font-semibold transition-all
            ${
              contentOpportunities.length > 0
                ? "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 shadow-lg"
                : "bg-gray-300 cursor-not-allowed"
            }
          `}
        >
          ✅ 选择内容，下一步
        </button>
      </div>
    </div>
  );
}
