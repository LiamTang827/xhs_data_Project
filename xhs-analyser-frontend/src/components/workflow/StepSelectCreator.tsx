"use client";

import { useState, useEffect } from "react";

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

interface Props {
  onCreatorSelected: (creator: Creator) => void;
}

/* ---- AddCreatorDialog ---- */
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
        <p className="text-sm text-gray-500">输入小红书用户 ID，系统将自动采集数据并加入创作者列表</p>
        <input
          className="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-purple-500 focus:outline-none"
          placeholder="输入小红书用户 ID"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
        />
        {error && <p className="text-sm text-red-500">{error}</p>}
        <div className="flex justify-end gap-3">
          <button onClick={onClose} className="rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-100">
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

export default function StepSelectCreator({ onCreatorSelected }: Props) {
  const [creators, setCreators] = useState<Creator[]>([]);
  const [selectedCreator, setSelectedCreator] = useState<Creator | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showAddDialog, setShowAddDialog] = useState(false);

  useEffect(() => {
    loadCreators();
  }, []);

  const loadCreators = async () => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
      const response = await fetch(`${API_URL}/api/style/creators`);

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      if (data.success && data.creators) {
        setCreators(data.creators);
        if (data.creators.length > 0 && !selectedCreator) {
          setSelectedCreator(data.creators[0]);
        }
      }
    } catch (err) {
      setError(`加载创作者失败: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="rounded-2xl border border-black/10 bg-white p-12 shadow-sm">
        <div className="flex flex-col items-center justify-center">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-purple-600 border-r-transparent"></div>
          <p className="mt-4 text-sm text-black/60">加载创作者列表中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-gradient-to-br from-purple-50 via-pink-50 to-purple-50 border border-purple-100 p-8 shadow-xs">
        <div className="flex items-start gap-3 mb-2">
          <span className="text-2xl">👤</span>
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-1">第一步：确认你的身份</h2>
            <p className="text-gray-600">选择你所代表的创作者账号，系统将基于这个身份为你推荐内容方向</p>
          </div>
        </div>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700 font-medium">
          ⚠️ {error}
        </div>
      )}

      {/* 创作者选择 */}
      <div className="rounded-2xl bg-white border border-black/5 p-8 shadow-xs">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">选择你的创作者账号</h3>
          <button
            onClick={() => setShowAddDialog(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 transition-colors"
          >
            <span className="text-lg">+</span>
            添加创作者
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {creators.map((creator) => (
            <button
              key={creator.user_id}
              onClick={() => setSelectedCreator(creator)}
              className={`
                p-4 rounded-xl border-2 transition-all text-left
                ${
                  selectedCreator?.user_id === creator.user_id
                    ? "border-purple-500 bg-purple-50 ring-2 ring-purple-200"
                    : "border-gray-200 bg-gray-50 hover:border-purple-300"
                }
              `}
            >
              <div className="flex items-start gap-3">
                {creator.avatar && (
                  <img
                    src={creator.avatar}
                    alt={creator.nickname}
                    className="w-12 h-12 rounded-full object-cover"
                  />
                )}
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-black truncate">{creator.nickname}</h3>
                  <p className="text-xs text-black/60 mt-1">
                    👥 {creator.followers.toLocaleString()} 粉丝
                  </p>
                  <p className="text-xs text-black/60">
                    💕 {creator.total_engagement.toLocaleString()} 互动
                  </p>
                  {creator.topics.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {creator.topics.slice(0, 3).map((topic, idx) => (
                        <span
                          key={idx}
                          className="inline-block bg-purple-100 text-purple-700 text-xs px-2 py-1 rounded"
                        >
                          {topic}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 选中创作者的详细信息 */}
      {selectedCreator && (
        <div className="rounded-2xl bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-200 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2"><span>📊</span> 你的创作者档案</h3>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {selectedCreator.followers.toLocaleString()}
              </div>
              <div className="text-xs text-black/60 mt-1">粉丝数</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-pink-600">
                {selectedCreator.total_engagement.toLocaleString()}
              </div>
              <div className="text-xs text-black/60 mt-1">总互动数</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {selectedCreator.note_count || 0}
              </div>
              <div className="text-xs text-black/60 mt-1">笔记数</div>
            </div>
          </div>
          <div className="mb-4">
            <div className="text-xs font-semibold text-black/60 mb-2">内容方向</div>
            <div className="flex flex-wrap gap-2">
              {selectedCreator.topics.map((topic, idx) => (
                <span
                  key={idx}
                  className="bg-white border border-blue-300 text-blue-700 text-sm px-3 py-1 rounded-full"
                >
                  {topic}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 继续按钮 */}
      <button
        onClick={() => selectedCreator && onCreatorSelected(selectedCreator)}
        disabled={!selectedCreator}
        className={`
          w-full rounded-lg px-6 py-4 text-white font-semibold transition-all
          ${
            selectedCreator
              ? "bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 shadow-lg hover:shadow-xl"
              : "bg-gray-300 cursor-not-allowed"
          }
        `}
      >
        ✓ 确认身份，下一步
      </button>

      {/* 添加创作者对话框 */}
      <AddCreatorDialog
        isOpen={showAddDialog}
        onClose={() => setShowAddDialog(false)}
        onSuccess={() => {
          setShowAddDialog(false);
          loadCreators(); // 重新加载列表
        }}
      />
    </div>
  );
}
