"use client";

import { useState, useEffect, useMemo } from "react";
import type { CreatorNode } from "@/data/creators";

/* ============================================================
   Type definitions
   ============================================================ */

interface Creator {
  nickname: string;
  name?: string;
  user_id: string;
  followers: number;
  total_engagement: number;
  note_count?: number;
  topics: string[];
  avatar?: string;
  style?: string;
  platform?: string;
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

interface CompetitorNote {
  id: string;
  title: string;
  desc: string;
  likes: number;
  collected_count: number;
  comments_count: number;
  share_count: number;
  engagement_score: number;
  create_time: number | null;
  type: string;
  images_list: { url: string }[];
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

/* ============================================================
   AddCreatorDialog
   ============================================================ */
function AddCreatorDialog({
  isOpen,
  onClose,
  onSuccess,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [userId, setUserId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async () => {
    if (!userId.trim()) return;
    setLoading(true);
    setError("");
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/api/creators/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId.trim() }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "添加失败");
      }
      setUserId("");
      onSuccess();
    } catch (e: any) {
      setError(e.message || "添加失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl space-y-4">
        <h3 className="text-lg font-semibold">添加创作者</h3>
        <p className="text-sm text-gray-500">
          输入小红书用户 ID，系统将自动采集数据并加入网络
        </p>
        <input
          className="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-purple-500 focus:outline-none"
          placeholder="输入小红书用户 ID"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
        />
        {error && <p className="text-sm text-red-500">{error}</p>}
        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-100"
          >
            取消
          </button>
          <button
            onClick={handleSubmit}
            disabled={loading || !userId.trim()}
            className="rounded-lg bg-purple-600 px-4 py-2 text-sm text-white hover:bg-purple-700 disabled:opacity-50"
          >
            {loading ? "添加中..." : "确认添加"}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ============================================================
   CreatorProfilePanel
   ============================================================ */
function CreatorProfilePanel({
  creator,
  networkNode,
  myCreator,
  onClose,
}: {
  creator: Creator;
  networkNode?: CreatorNode;
  myCreator: Creator;
  onClose: () => void;
}) {
  const desc = networkNode?.desc;
  const primaryTrack = networkNode?.primaryTrack;
  const contentForm = networkNode?.contentForm;
  const ipLocation = networkNode?.ipLocation;
  const redId = networkNode?.redId;
  const myTopics = new Set(myCreator.topics);

  return (
    <div className="rounded-2xl border border-purple-200 bg-gradient-to-br from-purple-50/80 to-white p-5 space-y-3">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          {creator.avatar ? (
            <img
              src={creator.avatar}
              alt={creator.nickname}
              className="w-12 h-12 rounded-xl object-cover ring-2 ring-purple-200"
            />
          ) : (
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white text-lg font-bold">
              {creator.nickname.charAt(0)}
            </div>
          )}
          <div>
            <h4 className="text-sm font-bold text-gray-900">{creator.nickname}</h4>
            <div className="flex items-center gap-2 mt-0.5">
              {redId && <span className="text-xs text-gray-400">ID: {redId}</span>}
              {ipLocation && <span className="text-xs text-gray-500">📍 {ipLocation}</span>}
            </div>
          </div>
        </div>
        <button
          onClick={onClose}
          className="rounded-lg p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors text-sm"
        >
          ✕
        </button>
      </div>

      {desc && (
        <p className="text-xs text-gray-600 leading-relaxed bg-white/80 rounded-lg p-2.5 border border-gray-100">
          {desc}
        </p>
      )}

      {/* Stats */}
      <div className="grid grid-cols-3 gap-1.5">
        <div className="rounded-lg bg-white border border-gray-100 p-2 text-center">
          <div className="text-sm font-bold text-purple-600">
            {creator.followers >= 10000
              ? (creator.followers / 10000).toFixed(1) + "万"
              : creator.followers.toLocaleString()}
          </div>
          <div className="text-xs text-gray-500">粉丝</div>
        </div>
        <div className="rounded-lg bg-white border border-gray-100 p-2 text-center">
          <div className="text-sm font-bold text-pink-600">
            {creator.total_engagement >= 10000
              ? (creator.total_engagement / 10000).toFixed(1) + "万"
              : creator.total_engagement.toLocaleString()}
          </div>
          <div className="text-xs text-gray-500">总互动</div>
        </div>
        <div className="rounded-lg bg-white border border-gray-100 p-2 text-center">
          <div className="text-sm font-bold text-blue-600">{creator.note_count || 0}</div>
          <div className="text-xs text-gray-500">笔记</div>
        </div>
      </div>

      {(primaryTrack || contentForm) && (
        <div className="space-y-1.5 text-xs">
          {primaryTrack && (
            <div className="flex items-center gap-2">
              <span className="text-gray-400 shrink-0">赛道</span>
              <span className="text-gray-800 bg-purple-50 px-2 py-0.5 rounded-md">{primaryTrack}</span>
            </div>
          )}
          {contentForm && contentForm !== "未知" && (
            <div className="flex items-start gap-2">
              <span className="text-gray-400 shrink-0">风格</span>
              <p className="text-gray-700 leading-relaxed">{contentForm}</p>
            </div>
          )}
        </div>
      )}

      {creator.topics.length > 0 && (
        <div>
          <h5 className="text-xs font-medium text-gray-400 mb-1.5">内容标签</h5>
          <div className="flex flex-wrap gap-1">
            {creator.topics.map((topic, idx) => {
              const isCommon = myTopics.has(topic);
              return (
                <span
                  key={idx}
                  className={`text-xs px-1.5 py-0.5 rounded-full ${
                    isCommon ? "bg-green-100 text-green-700 font-medium" : "bg-blue-50 text-blue-600"
                  }`}
                >
                  {isCommon && "✓ "}
                  {topic}
                </span>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

/* ============================================================
   Main: StepMatchCreators (combined: 匹配博主 + 发现爆品)
   ============================================================ */
export default function StepMatchCreators({
  myCreator,
  selectedCompetitor,
  contentOpportunities,
  minEngagement,
  topN,
  days,
  onCompetitorSelected,
  onContentDiscovered,
  onContentSelected,
  onParameterChange,
  onBack,
}: Props) {
  /* ---- Network data (profile enrichment only — no graph) ---- */
  const [networkCreators, setNetworkCreators] = useState<CreatorNode[]>([]);

  /* ---- Similar creators from /api/style/creators (real stats) ---- */
  const [styleCreators, setStyleCreators] = useState<Creator[]>([]);
  const [styleLoading, setStyleLoading] = useState(true);

  /* ---- Embedding similarity scores ---- */
  const [similarityScores, setSimilarityScores] = useState<Record<string, number>>({});

  /* ---- UI state ---- */
  const [selectedCreatorId, setSelectedCreatorId] = useState<string | null>(
    selectedCompetitor?.user_id || null
  );
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [activeTab, setActiveTab] = useState<"analyze" | "search">("analyze");

  /* ---- Analysis state ---- */
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  /* ---- Competitor notes state ---- */
  const [competitorNotes, setCompetitorNotes] = useState<CompetitorNote[]>([]);
  const [notesLoading, setNotesLoading] = useState(false);
  const [notesTotal, setNotesTotal] = useState(0);
  const [notesSortBy, setNotesSortBy] = useState<"engagement" | "latest">("engagement");
  const [copiedNoteId, setCopiedNoteId] = useState<string | null>(null);

  /* ---- Note search state ---- */
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<NoteSearchResult[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [searchMeta, setSearchMeta] = useState<{
    total: number;
    search_time_ms: number;
    index_size: number;
  } | null>(null);

  /* ---- Data loaders ---- */
  const loadNetwork = async () => {
    try {
      const res = await fetch("/api/creators");
      if (!res.ok) return;
      const ct = res.headers.get("content-type") || "";
      if (!ct.includes("application/json")) return;
      const json = await res.json();
      if (Array.isArray(json.creators)) setNetworkCreators(json.creators);
    } catch {}
  };

  const loadStyleCreators = async () => {
    setStyleLoading(true);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/api/style/creators`);
      if (!res.ok) throw new Error();
      const data = await res.json();
      if (data.success && data.creators) {
        setStyleCreators(
          data.creators.filter((c: Creator) => c.user_id !== myCreator.user_id)
        );
      }
    } catch {}
    finally { setStyleLoading(false); }
  };

  const loadSimilarities = async () => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/api/creators/similarities/${myCreator.user_id}`);
      if (!res.ok) return;
      const data = await res.json();
      if (data.success && data.similarities) setSimilarityScores(data.similarities);
    } catch {}
  };

  const loadCompetitorNotes = async (userId: string) => {
    setNotesLoading(true);
    setCompetitorNotes([]);
    setNotesTotal(0);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
      const params = new URLSearchParams({
        limit: "30",
        sort: notesSortBy,
      });
      if (days) params.set("days", String(days));
      const res = await fetch(`${API_URL}/api/creators/${userId}/notes?${params}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (data.success) {
        setCompetitorNotes(data.notes || []);
        setNotesTotal(data.total || 0);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "获取笔记失败");
    } finally {
      setNotesLoading(false);
    }
  };

  useEffect(() => {
    loadNetwork();
    loadStyleCreators();
    loadSimilarities();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [myCreator.user_id]);

  /* Auto-fetch notes when competitor or sort/days changes */
  useEffect(() => {
    if (selectedCompetitor) {
      loadCompetitorNotes(selectedCompetitor.user_id);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCompetitor?.user_id, notesSortBy, days]);

  /* ---- Similarity helpers ---- */
  const getScore = (userId: string, topics: string[]): number => {
    if (Object.keys(similarityScores).length > 0) return similarityScores[userId] ?? 0;
    const myTopics = new Set(myCreator.topics);
    if (myTopics.size === 0) return 0;
    const union = new Set([...myTopics, ...topics]).size;
    const intersection = [...myTopics].filter((t) => topics.includes(t)).length;
    return union === 0 ? 0 : intersection / union;
  };

  const sortedCreators = useMemo(() => {
    return [...styleCreators].sort(
      (a, b) => getScore(b.user_id, b.topics) - getScore(a.user_id, a.topics)
    );
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [styleCreators, similarityScores, myCreator.topics]);

  const selectedCreator = useMemo(
    () => sortedCreators.find((c) => c.user_id === selectedCreatorId) || null,
    [sortedCreators, selectedCreatorId]
  );

  const selectedNetworkNode = useMemo(
    () => networkCreators.find((n) => n.id === selectedCreatorId) || undefined,
    [networkCreators, selectedCreatorId]
  );

  const usingEmbedding = Object.keys(similarityScores).length > 0;

  /* ---- Handlers ---- */
  const handleCreatorCard = (creator: Creator) => {
    setSelectedCreatorId(creator.user_id);
    onCompetitorSelected(creator);
  };

  const handleCopyNote = async (note: CompetitorNote) => {
    const text = `${note.title}\n\n${note.desc}`;
    try {
      await navigator.clipboard.writeText(text);
      setCopiedNoteId(note.id);
      setTimeout(() => setCopiedNoteId(null), 2000);
    } catch {
      // fallback
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      setCopiedNoteId(note.id);
      setTimeout(() => setCopiedNoteId(null), 2000);
    }
  };

  const handleSelectNote = (note: CompetitorNote) => {
    const opportunity: ContentOpportunity = {
      note_title: note.title || "(无标题)",
      note_id: note.id,
      engagement_index: note.engagement_score / 1000,
      engagement_count: note.likes + note.collected_count + note.comments_count,
      reason: `来自 ${selectedCompetitor?.nickname || "对标博主"} 的高互动笔记`,
      direction: note.desc ? note.desc.slice(0, 300) : "",
      angles: [],
    };
    onContentSelected(opportunity);
  };

  /* Topic overlap computation */
  const topicOverlap = useMemo(() => {
    if (!selectedCompetitor) return { common: [] as string[], myOnly: [] as string[], theirOnly: [] as string[] };

    const myTopics = new Set(myCreator.topics || []);
    // Also try enriching from networkCreators
    const myNode = networkCreators.find((n) => n.id === myCreator.user_id);
    if (myNode?.topics) myNode.topics.forEach((t) => myTopics.add(t));

    const theirTopics = new Set(selectedCompetitor.topics || []);
    const theirNode = networkCreators.find((n) => n.id === selectedCompetitor.user_id);
    if (theirNode?.topics) theirNode.topics.forEach((t) => theirTopics.add(t));

    const common: string[] = [];
    const myOnly: string[] = [];
    const theirOnly: string[] = [];

    myTopics.forEach((t) => {
      if (theirTopics.has(t)) common.push(t);
      else myOnly.push(t);
    });
    theirTopics.forEach((t) => {
      if (!myTopics.has(t)) theirOnly.push(t);
    });

    return { common, myOnly, theirOnly };
  }, [selectedCompetitor, myCreator, networkCreators]);

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

  /* ============================================================
     Render
     ============================================================ */
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-2xl bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <span>🔮</span> 第二步：发现灵感
            </h2>
            <p className="text-black/60 mt-1">
              选择对标博主，查看其爆款笔记与内容重合分析；或直接语义搜索全库笔记
            </p>
          </div>
          <button
            onClick={() => setShowAddDialog(true)}
            className="inline-flex items-center gap-1.5 rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 transition-colors shadow-sm"
          >
            <span className="text-lg leading-none">+</span> 添加创作者
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-600">
          ❌ {error}
        </div>
      )}

      {/* ===== Main 2-column layout ===== */}
      <div className="flex gap-5 items-start">

        {/* ---- LEFT: Creator list ---- */}
        <div className="w-72 shrink-0 flex flex-col gap-4">
          <div
            className="rounded-2xl bg-white border border-black/5 shadow-sm overflow-hidden flex flex-col"
            style={{ maxHeight: "560px" }}
          >
            <div className="p-4 border-b border-gray-100 bg-gray-50/50 flex items-center justify-between">
              <h3 className="font-semibold text-gray-900 text-sm">
                相似博主{" "}
                <span className="text-purple-500 font-normal ml-1">{sortedCreators.length}</span>
              </h3>
              {usingEmbedding && (
                <span className="text-[10px] text-purple-400 bg-purple-50 px-1.5 py-0.5 rounded-full">
                  AI排序
                </span>
              )}
            </div>

            <div className="overflow-y-auto flex-1 p-2 space-y-1.5">
              {styleLoading ? (
                <div className="flex justify-center py-8">
                  <div className="inline-block h-6 w-6 animate-spin rounded-full border-2 border-solid border-purple-600 border-r-transparent" />
                </div>
              ) : sortedCreators.length === 0 ? (
                <div className="text-center py-8 text-gray-400 text-sm">暂无相似博主</div>
              ) : (
                sortedCreators.map((creator) => {
                  const similarity = getScore(creator.user_id, creator.topics);
                  const isActive = selectedCompetitor?.user_id === creator.user_id;

                  return (
                    <button
                      key={creator.user_id}
                      onClick={() => handleCreatorCard(creator)}
                      className={`
                        w-full text-left rounded-xl border p-3 transition-all
                        ${isActive
                          ? "border-purple-400 bg-purple-50 shadow ring-1 ring-purple-200"
                          : "border-transparent hover:border-purple-200 hover:bg-purple-50/40"
                        }
                      `}
                    >
                      <div className="flex items-center gap-3">
                        {creator.avatar ? (
                          <img
                            src={creator.avatar}
                            alt={creator.nickname}
                            className="w-10 h-10 rounded-lg object-cover shrink-0"
                          />
                        ) : (
                          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-300 to-pink-300 flex items-center justify-center text-white text-sm font-bold shrink-0">
                            {creator.nickname.charAt(0)}
                          </div>
                        )}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-1">
                            <h4 className="font-medium text-gray-900 text-sm truncate">
                              {creator.nickname}
                            </h4>
                            <span
                              title={usingEmbedding ? "内容 embedding 向量相似度" : "话题标签 Jaccard 相似度"}
                              className="text-xs font-semibold text-purple-500 shrink-0 flex items-center gap-0.5"
                            >
                              {(similarity * 100).toFixed(0)}%
                              <span className="text-purple-300 text-[9px]">
                                {usingEmbedding ? "·AI" : "·tag"}
                              </span>
                            </span>
                          </div>
                          <div className="flex items-center gap-3 text-xs text-gray-500 mt-0.5">
                            <span>
                              {creator.followers >= 10000
                                ? (creator.followers / 10000).toFixed(1) + "万粉"
                                : creator.followers.toLocaleString() + "粉"}
                            </span>
                            <span>{(creator.note_count || 0).toLocaleString()}篇</span>
                          </div>
                        </div>
                      </div>
                    </button>
                  );
                })
              )}
            </div>
          </div>

          {/* Profile panel appears when a creator is selected */}
          {selectedCreator && (
            <CreatorProfilePanel
              creator={selectedCreator}
              networkNode={selectedNetworkNode}
              myCreator={myCreator}
              onClose={() => setSelectedCreatorId(null)}
            />
          )}
        </div>

        {/* ---- RIGHT: Analysis panel ---- */}
        <div className="flex-1 min-w-0 space-y-4">

          {/* Tab bar (always visible) */}
          <div className="flex rounded-xl bg-gray-100 p-1">
            <button
              onClick={() => setActiveTab("analyze")}
              className={`flex-1 rounded-lg px-4 py-2.5 text-sm font-semibold transition-all ${
                activeTab === "analyze"
                  ? "bg-white text-purple-700 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              🎯 对标分析
            </button>
            <button
              onClick={() => setActiveTab("search")}
              className={`flex-1 rounded-lg px-4 py-2.5 text-sm font-semibold transition-all ${
                activeTab === "search"
                  ? "bg-white text-purple-700 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              🔍 笔记语义搜索
            </button>
          </div>

          {/* ========== Tab: 对标分析 ========== */}
          {activeTab === "analyze" && (
            <>
              {!selectedCompetitor ? (
                <div className="rounded-2xl bg-white border border-black/5 shadow-sm min-h-[360px] flex flex-col items-center justify-center text-gray-400">
                  <div className="text-5xl mb-4">←</div>
                  <p className="text-sm font-medium">从左侧选择一位对标博主</p>
                  <p className="text-xs mt-1 text-gray-400">选择博主后将展示其爆款笔记与内容重合分析</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Competitor mini strip */}
                  <div className="rounded-xl bg-white border border-black/5 shadow-sm px-4 py-3 flex items-center gap-3">
                    {selectedCompetitor.avatar ? (
                      <img
                        src={selectedCompetitor.avatar}
                        alt={selectedCompetitor.nickname}
                        className="w-9 h-9 rounded-lg object-cover shrink-0"
                      />
                    ) : (
                      <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-white text-sm font-bold shrink-0">
                        {selectedCompetitor.nickname.charAt(0)}
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <span className="font-semibold text-gray-900 text-sm">
                        {selectedCompetitor.nickname}
                      </span>
                      <div className="flex items-center gap-3 text-xs text-gray-400 mt-0.5">
                        <span>
                          {selectedCompetitor.followers >= 10000
                            ? (selectedCompetitor.followers / 10000).toFixed(1) + "万粉丝"
                            : selectedCompetitor.followers.toLocaleString() + "粉丝"}
                        </span>
                        <span>
                          总互动{" "}
                          {selectedCompetitor.total_engagement >= 10000
                            ? (selectedCompetitor.total_engagement / 10000).toFixed(1) + "万"
                            : selectedCompetitor.total_engagement.toLocaleString()}
                        </span>
                      </div>
                    </div>
                    <span className="text-xs text-purple-400 shrink-0">正在对标 ▼</span>
                  </div>

                  {/* ---- Topic overlap section ---- */}
                  {(topicOverlap.common.length > 0 || topicOverlap.myOnly.length > 0 || topicOverlap.theirOnly.length > 0) && (
                    <div className="rounded-xl bg-white border border-black/5 shadow-sm p-4 space-y-3">
                      <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-1.5">
                        <span>🔗</span> 内容领域重合分析
                      </h3>

                      {topicOverlap.common.length > 0 && (
                        <div>
                          <div className="text-xs text-gray-500 mb-1.5">
                            共同领域 <span className="text-green-600 font-semibold">({topicOverlap.common.length})</span>
                          </div>
                          <div className="flex flex-wrap gap-1.5">
                            {topicOverlap.common.map((t) => (
                              <span key={t} className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700 font-medium">
                                ✓ {t}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="grid grid-cols-2 gap-3">
                        {topicOverlap.myOnly.length > 0 && (
                          <div>
                            <div className="text-xs text-gray-400 mb-1">我的独有</div>
                            <div className="flex flex-wrap gap-1">
                              {topicOverlap.myOnly.map((t) => (
                                <span key={t} className="text-xs px-1.5 py-0.5 rounded-full bg-purple-50 text-purple-600">{t}</span>
                              ))}
                            </div>
                          </div>
                        )}
                        {topicOverlap.theirOnly.length > 0 && (
                          <div>
                            <div className="text-xs text-gray-400 mb-1">对方独有 <span className="text-orange-500">(可借鉴)</span></div>
                            <div className="flex flex-wrap gap-1">
                              {topicOverlap.theirOnly.map((t) => (
                                <span key={t} className="text-xs px-1.5 py-0.5 rounded-full bg-orange-50 text-orange-600">{t}</span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>

                      {topicOverlap.common.length > 0 && (
                        <p className="text-xs text-gray-400 bg-gray-50 rounded-lg px-3 py-2">
                          💡 你们在 <strong className="text-gray-700">{topicOverlap.common.join("、")}</strong> 方面内容高度重合，
                          可以重点参考 TA 在这些领域的爆款笔记
                        </p>
                      )}
                    </div>
                  )}

                  {/* ---- Controls: time range + sort ---- */}
                  <div className="rounded-xl bg-white border border-black/5 shadow-sm px-4 py-3 flex items-center gap-4 flex-wrap">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500">时间</span>
                      <div className="flex rounded-lg bg-gray-100 p-0.5">
                        {[
                          { label: "近一周", value: 7 },
                          { label: "近一月", value: 30 },
                          { label: "全部", value: null },
                        ].map((opt) => (
                          <button
                            key={opt.label}
                            onClick={() => onParameterChange({ days: opt.value })}
                            className={`text-xs font-medium px-2.5 py-1 rounded-md transition-all ${
                              days === opt.value
                                ? "bg-white text-purple-700 shadow-sm"
                                : "text-gray-500 hover:text-gray-700"
                            }`}
                          >
                            {opt.label}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500">排序</span>
                      <div className="flex rounded-lg bg-gray-100 p-0.5">
                        {[
                          { label: "🔥 爆款优先", value: "engagement" as const },
                          { label: "🕐 最新优先", value: "latest" as const },
                        ].map((opt) => (
                          <button
                            key={opt.value}
                            onClick={() => setNotesSortBy(opt.value)}
                            className={`text-xs font-medium px-2.5 py-1 rounded-md transition-all ${
                              notesSortBy === opt.value
                                ? "bg-white text-purple-700 shadow-sm"
                                : "text-gray-500 hover:text-gray-700"
                            }`}
                          >
                            {opt.label}
                          </button>
                        ))}
                      </div>
                    </div>
                    {notesTotal > 0 && (
                      <span className="text-xs text-gray-400 ml-auto">
                        共 {notesTotal} 篇笔记
                      </span>
                    )}
                  </div>

                  {/* ---- Notes list ---- */}
                  {notesLoading && (
                    <div className="rounded-2xl bg-white border border-black/10 p-12 shadow-sm flex flex-col items-center">
                      <div className="inline-block h-10 w-10 animate-spin rounded-full border-4 border-solid border-purple-600 border-r-transparent" />
                      <p className="mt-4 text-sm text-black/60">加载笔记中...</p>
                    </div>
                  )}

                  {!notesLoading && competitorNotes.length > 0 && (
                    <div className="space-y-3">
                      <h3 className="text-sm font-bold text-gray-900 px-1 flex items-center gap-2">
                        <span>📝</span> 爆款笔记
                        <span className="text-xs font-normal text-gray-400 ml-1">
                          点击「选择」进入文案生成
                        </span>
                      </h3>
                      {competitorNotes.map((note, idx) => (
                        <div
                          key={note.id}
                          className="rounded-2xl border border-black/10 bg-white p-4 shadow-sm hover:shadow-md hover:border-purple-200 transition-all"
                        >
                          <div className="flex items-start gap-3">
                            {/* Rank badge */}
                            <div className="flex flex-col items-center gap-1 min-w-[36px] pt-0.5">
                              <div className={`text-sm font-bold ${idx < 3 ? "text-orange-500" : "text-gray-400"}`}>
                                #{idx + 1}
                              </div>
                            </div>

                            {/* Content */}
                            <div className="flex-1 min-w-0">
                              <h4 className="text-sm font-semibold text-gray-900 mb-1 line-clamp-2">
                                {note.title || "(无标题)"}
                              </h4>
                              {note.desc && (
                                <p className="text-xs text-gray-600 line-clamp-3 mb-2 leading-relaxed">
                                  {note.desc}
                                </p>
                              )}
                              {/* Engagement stats */}
                              <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500">
                                <span>👍 {note.likes.toLocaleString()}</span>
                                <span>💾 {note.collected_count.toLocaleString()}</span>
                                <span>💬 {note.comments_count.toLocaleString()}</span>
                                {note.share_count > 0 && <span>🔗 {note.share_count.toLocaleString()}</span>}
                                <span className="text-orange-500 font-semibold">
                                  互动 {note.engagement_score.toLocaleString()}
                                </span>
                                {note.create_time && (
                                  <span className="text-gray-400">
                                    {new Date(note.create_time * 1000).toLocaleDateString("zh-CN")}
                                  </span>
                                )}
                              </div>
                            </div>

                            {/* Actions */}
                            <div className="flex flex-col gap-2 shrink-0">
                              <button
                                onClick={() => handleCopyNote(note)}
                                className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                                  copiedNoteId === note.id
                                    ? "bg-green-100 text-green-700"
                                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                                }`}
                              >
                                {copiedNoteId === note.id ? "✓ 已复制" : "📋 复制"}
                              </button>
                              <button
                                onClick={() => handleSelectNote(note)}
                                className="rounded-lg bg-purple-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-purple-700 transition-all"
                              >
                                选择 →
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {!notesLoading && competitorNotes.length === 0 && (
                    <div className="rounded-2xl bg-white border border-black/10 p-12 shadow-sm flex flex-col items-center text-black/40">
                      <div className="text-4xl mb-3">📭</div>
                      <p className="text-sm">该博主暂无笔记数据</p>
                    </div>
                  )}
                </div>
              )}
            </>
          )}

          {/* ========== Tab: 笔记语义搜索 ========== */}
          {activeTab === "search" && (
            <div className="space-y-4">
              <div className="rounded-2xl bg-white border border-black/10 p-5 shadow-sm">
                <p className="text-xs text-gray-500 mb-3">
                  系统将把你的搜索词转化为向量，与所有笔记内容进行语义相似度匹配（不限于关键词）
                </p>
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleNoteSearch()}
                    placeholder="例如：AI教程、旅行攻略、美食推荐、职场干货..."
                    className="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20"
                  />
                  <button
                    onClick={handleNoteSearch}
                    disabled={searchLoading || !searchQuery.trim()}
                    className="rounded-lg bg-purple-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
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

              {searchMeta && (
                <div className="flex items-center gap-4 text-xs text-gray-500 px-1">
                  <span>
                    找到 <strong className="text-purple-600">{searchMeta.total}</strong> 条结果
                  </span>
                  <span>•</span>
                  <span>耗时 {searchMeta.search_time_ms}ms</span>
                  <span>•</span>
                  <span>索引 {searchMeta.index_size} 条笔记</span>
                </div>
              )}

              {searchLoading && (
                <div className="rounded-2xl bg-white border border-black/10 p-12 shadow-sm flex flex-col items-center">
                  <div className="inline-block h-10 w-10 animate-spin rounded-full border-4 border-solid border-purple-600 border-r-transparent" />
                  <p className="mt-4 text-sm text-black/60">语义搜索中...</p>
                </div>
              )}

              {!searchLoading && searchResults.length > 0 && (
                <div className="space-y-3">
                  {searchResults.map((note, idx) => (
                    <button
                      key={note.note_id}
                      onClick={() => selectSearchResult(note)}
                      className="w-full rounded-2xl border border-black/10 bg-white p-4 shadow-sm hover:shadow-md hover:border-purple-300 transition-all text-left group"
                    >
                      <div className="flex items-start gap-3">
                        <div className="flex flex-col items-center gap-1 min-w-[44px]">
                          <div className="text-base font-bold text-gray-400">#{idx + 1}</div>
                          <div
                            className={`text-xs font-bold px-1.5 py-0.5 rounded-full ${
                              note.similarity >= 0.8
                                ? "bg-green-100 text-green-700"
                                : note.similarity >= 0.6
                                ? "bg-yellow-100 text-yellow-700"
                                : "bg-gray-100 text-gray-600"
                            }`}
                          >
                            {(note.similarity * 100).toFixed(0)}%
                          </div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="text-sm font-semibold text-black mb-1 line-clamp-2">
                            {note.title || "(无标题)"}
                          </h4>
                          <div className="flex items-center gap-2 mb-1.5">
                            {note.avatar && (
                              <img
                                src={note.avatar}
                                alt={note.nickname}
                                className="w-4 h-4 rounded-full object-cover"
                              />
                            )}
                            <span className="text-xs text-gray-500">{note.nickname || "未知"}</span>
                          </div>
                          {note.desc && (
                            <p className="text-xs text-gray-600 line-clamp-2 mb-2">{note.desc}</p>
                          )}
                          <div className="flex flex-wrap gap-3 text-xs text-gray-500">
                            <span>👍 {note.likes.toLocaleString()}</span>
                            <span>💾 {note.collected_count.toLocaleString()}</span>
                            <span>💬 {note.comments_count.toLocaleString()}</span>
                            {note.share_count > 0 && (
                              <span>🔗 {note.share_count.toLocaleString()}</span>
                            )}
                          </div>
                        </div>
                        <div className="text-purple-400 text-sm self-center shrink-0 group-hover:text-purple-600">
                          选择 →
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {!searchLoading && searchResults.length === 0 && !searchMeta && (
                <div className="rounded-2xl bg-white border border-black/10 p-12 shadow-sm flex flex-col items-center text-black/40">
                  <div className="text-4xl mb-3">🔍</div>
                  <p className="text-sm mb-1">输入关键词，在全库笔记中语义搜索</p>
                  <p className="text-xs text-gray-400">支持自然语言：如「如何用 AI 做内容」</p>
                </div>
              )}

              {!searchLoading && searchResults.length === 0 && searchMeta && (
                <div className="rounded-2xl bg-white border border-black/10 p-12 shadow-sm flex flex-col items-center text-black/40">
                  <div className="text-4xl mb-3">📭</div>
                  <p className="text-sm">未找到匹配笔记，换个关键词试试？</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Back button */}
      <div className="pt-2">
        <button
          onClick={onBack}
          className="rounded-lg border border-black/20 px-6 py-3.5 text-black font-semibold hover:bg-gray-50 transition-colors"
        >
          ← 上一步
        </button>
      </div>

      {/* Add creator dialog */}
      <AddCreatorDialog
        isOpen={showAddDialog}
        onClose={() => setShowAddDialog(false)}
        onSuccess={() => {
          setShowAddDialog(false);
          loadNetwork();
          loadStyleCreators();
        }}
      />
    </div>
  );
}
