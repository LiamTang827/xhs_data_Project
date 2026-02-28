"use client";

import { useMemo, useState } from "react";
import type { CreatorEdge, CreatorNode } from "@/data/creators";
import { CreatorNetworkGraph } from "./CreatorNetworkGraph";

/* ---- Inline CreatorDetailPanel (was in deprecated/) ---- */
function CreatorDetailPanel({ node }: { node?: CreatorNode }) {
  if (!node) {
    return (
      <div className="rounded-xl border border-gray-200 bg-white p-6 text-center text-gray-400">
        点击网络图中的节点查看创作者详情
      </div>
    );
  }
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 space-y-4">
      <div className="flex items-center gap-3">
        {node.avatar && (
          <img src={node.avatar} alt={node.name} className="h-12 w-12 rounded-full object-cover" />
        )}
        <div>
          <h4 className="text-lg font-semibold text-gray-900">{node.name}</h4>
          {node.ipLocation && <span className="text-xs text-gray-500">{node.ipLocation}</span>}
        </div>
      </div>
      {node.desc && <p className="text-sm text-gray-600">{node.desc}</p>}
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div className="rounded-lg bg-gray-50 p-3">
          <div className="text-gray-500">粉丝</div>
          <div className="font-semibold">{node.followers?.toLocaleString() ?? "-"}</div>
        </div>
        <div className="rounded-lg bg-gray-50 p-3">
          <div className="text-gray-500">赛道</div>
          <div className="font-semibold">{node.primaryTrack || "-"}</div>
        </div>
      </div>
      {node.contentForm && (
        <div className="text-sm">
          <span className="text-gray-500">内容形式：</span>
          <span className="text-gray-700">{node.contentForm}</span>
        </div>
      )}
    </div>
  );
}

/* ---- Inline AddCreatorDialog (was in deprecated/) ---- */
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
        <input
          className="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none"
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
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "添加中..." : "确认添加"}
          </button>
        </div>
      </div>
    </div>
  );
}

interface CreatorUniverseProps {
  creators: CreatorNode[];
  edges: CreatorEdge[];
  clusters: Record<string, string[]>;
  trendingKeywords: Array<{
    topic: string;
    creators: string[];
    intensity: number;
  }>;
  onCreatorAdded?: () => void;
}

export function CreatorUniverse({
  creators,
  edges,
  clusters,
  onCreatorAdded,
}: CreatorUniverseProps) {
  const [selectedCreator, setSelectedCreator] = useState<string | undefined>(creators[0]?.id);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [similarityThreshold, setSimilarityThreshold] = useState(0.5);

  const handleRefreshNetwork = async () => {
    try {
      setIsRefreshing(true);
      const API_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/api/creators/network/refresh?similarity_threshold=${similarityThreshold}`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('刷新网络失败');
      }
      
      const data = await response.json();
      
      // 显示成功消息
      alert(data.message || '网络数据正在后台更新，请等待约30秒...');
      
      // 等待脚本完成（约30秒）后自动刷新数据
      setTimeout(() => {
        onCreatorAdded?.();
        setIsRefreshing(false);
      }, 35000); // 35秒，确保脚本有足够时间完成
    } catch (error) {
      console.error('刷新网络失败:', error);
      alert('刷新网络失败，请稍后重试');
      setIsRefreshing(false);
    }
  };

  const selectedNode = useMemo(
    () => creators.find((creator) => creator.id === selectedCreator),
    [creators, selectedCreator]
  );

  const nameLookup = useMemo(() => {
    const map = new Map<string, string>();
    creators.forEach((creator) => {
      map.set(creator.id, creator.name);
    });
    return map;
  }, [creators]);

  return (
    <div className="space-y-8">
      {/* 网络图 + 详情面板 */}
      <section>
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="text-xl font-semibold text-black">创作者关系网络</h3>
            <div className="text-sm text-gray-500 mt-1">
              {creators.length} 位创作者 • {edges.length} 条连接
            </div>
          </div>
          <div className="flex items-center gap-4">
            {/* 相似度阈值控制器 */}
            <div className="flex items-center gap-3 px-4 py-2 bg-gray-50 rounded-lg border border-gray-200">
              <label htmlFor="similarity-threshold" className="text-sm font-medium text-gray-700 whitespace-nowrap">
                相似度阈值
              </label>
              <input
                id="similarity-threshold"
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={similarityThreshold}
                onChange={(e) => setSimilarityThreshold(parseFloat(e.target.value))}
                className="w-32 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                disabled={isRefreshing}
              />
              <span className="text-sm font-semibold text-blue-600 w-10 text-center">
                {similarityThreshold.toFixed(2)}
              </span>
            </div>
            
            <button
              onClick={handleRefreshNetwork}
              disabled={isRefreshing}
              className="inline-flex items-center gap-2 rounded-lg bg-gray-600 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className={isRefreshing ? "animate-spin" : ""}>🔄</span>
              {isRefreshing ? '刷新中...' : '刷新网络'}
            </button>
            <button
              onClick={() => setShowAddDialog(true)}
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
            >
              <span className="text-lg">+</span>
              添加创作者
            </button>
          </div>
        </div>
        <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
          <CreatorNetworkGraph
            nodes={creators}
            edges={edges}
            activeId={selectedCreator}
            onNodeSelect={setSelectedCreator}
          />
          <div className="space-y-6">
            <CreatorDetailPanel node={selectedNode} />
          </div>
        </div>
      </section>

      {/* 添加创作者对话框 */}
      <AddCreatorDialog
        isOpen={showAddDialog}
        onClose={() => setShowAddDialog(false)}
        onSuccess={() => {
          setShowAddDialog(false);
          onCreatorAdded?.();
        }}
      />
    </div>
  );
}
