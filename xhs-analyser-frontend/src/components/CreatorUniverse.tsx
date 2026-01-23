"use client";

import { useMemo, useState } from "react";
import type { CreatorEdge, CreatorNode } from "@/data/creators";
import { CreatorNetworkGraph } from "./CreatorNetworkGraph";
import { CreatorDetailPanel } from "./CreatorDetailPanel";
import { TrendingTopics } from "./TrendingTopics";
import { FollowingAnalysis } from "./FollowingAnalysis";
import { GrowthPath } from "./GrowthPath";
import { trendingTopicsData } from "@/data/trending";

interface CreatorUniverseProps {
  creators: CreatorNode[];
  edges: CreatorEdge[];
  clusters: Record<string, string[]>;
  trendingKeywords: Array<{
    topic: string;
    creators: string[];
    intensity: number;
  }>;
}

export function CreatorUniverse({
  creators,
  edges,
  clusters,
}: CreatorUniverseProps) {
  const [selectedCreator, setSelectedCreator] = useState<string | undefined>(creators[0]?.id);

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
        <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
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

      {/* 成长路径推荐 */}
      <section id="growth">
        <GrowthPath
          userProfile={{
            estimatedFollowers: 3000,
            interestedTracks: ["美妆", "时尚"],
          }}
          followingCreators={creators}
          onSelectCreator={setSelectedCreator}
        />
      </section>

      {/* 流量密码榜 (暂时隐藏) */}
      {/* <TrendingTopics
        data={trendingTopicsData}
        renderCreatorTag={(creatorId) => nameLookup.get(creatorId) ?? creatorId}
      /> */}

      {/* 关注圈分析 (暂时隐藏) */}
      {/* <FollowingAnalysis 
        clusters={clusters} 
        nodes={creators} 
        onSelect={setSelectedCreator} 
      /> */}
    </div>
  );
}
