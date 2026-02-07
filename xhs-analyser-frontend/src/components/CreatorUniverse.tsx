"use client";

import { useMemo, useState } from "react";
import type { CreatorEdge, CreatorNode } from "@/data/creators";
import { CreatorNetworkGraph } from "./CreatorNetworkGraph";
import { CreatorDetailPanel } from "./CreatorDetailPanel";
import AddCreatorDialog from "./AddCreatorDialog";

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
          <h3 className="text-xl font-semibold text-black">创作者关系网络</h3>
          <button
            onClick={() => setShowAddDialog(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
          >
            <span className="text-lg">+</span>
            添加创作者
          </button>
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
