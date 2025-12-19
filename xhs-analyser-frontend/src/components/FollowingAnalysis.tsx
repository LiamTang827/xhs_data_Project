import type { CreatorNode } from "@/data/creators";

interface FollowingAnalysisProps {
  clusters: Record<string, string[]>;
  nodes: CreatorNode[];
  onSelect: (id: string) => void;
}

interface TrackInsight {
  contentGaps: string[];
  avgFollowers: number;
  avgEngagement: number;
  recommendation: string;
}

const getTrackInsights = (creators: CreatorNode[]): TrackInsight => {
  if (creators.length === 0) {
    return {
      contentGaps: [],
      avgFollowers: 0,
      avgEngagement: 0,
      recommendation: "",
    };
  }

  const avgFollowers = creators.reduce((sum, c) => sum + c.followers, 0) / creators.length;
  const avgEngagement =
    creators.reduce((sum, c) => sum + c.engagementIndex, 0) / creators.length;

  // 分析内容空白区（这里是示例逻辑，实际应该基于更复杂的算法）
  const allKeywords = creators.flatMap((c) => c.recentKeywords);
  const keywordCounts = allKeywords.reduce(
    (acc, keyword) => {
      acc[keyword] = (acc[keyword] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  // 找出被多次提及的关键词（热点）
  const hotKeywords = Object.entries(keywordCounts)
    .filter(([_, count]) => count >= 2)
    .map(([keyword]) => keyword);

  // 生成内容空白区建议
  const contentGaps: string[] = [];
  if (creators.length >= 2) {
    contentGaps.push(`${hotKeywords[0] || "热门话题"}的平价版本`);
    contentGaps.push(`${creators[0].primaryTrack}新手入门系列`);
  }

  return {
    contentGaps,
    avgFollowers,
    avgEngagement,
    recommendation: `这个赛道平均粉丝 ${Math.round(avgFollowers / 10000)}万，互动率 ${avgEngagement.toFixed(1)}%`,
  };
};

export function FollowingAnalysis({ clusters, nodes, onSelect }: FollowingAnalysisProps) {
  const findNode = (id: string) => nodes.find((node) => node.id === id);

  return (
    <section className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm">
      <header className="mb-6">
        <h2 className="text-2xl font-semibold text-black">📊 你的关注圈分析</h2>
        <p className="mt-2 text-sm text-black/60">
          分析你关注的创作者，帮你找到自己的定位和内容方向
        </p>
      </header>

      <div className="space-y-6">
        {Object.entries(clusters).map(([track, creatorIds]) => {
          const creators = creatorIds
            .map((id) => findNode(id))
            .filter((c): c is CreatorNode => c !== null);

          const insights = getTrackInsights(creators);

          return (
            <div
              key={track}
              className="rounded-xl border-2 border-black/10 bg-gradient-to-br from-white to-gray-50 p-5"
            >
              {/* 赛道标题 */}
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-black">【{track}赛道】</h3>
                  <p className="text-sm text-black/50">
                    你关注了 {creators.length} 位创作者
                  </p>
                </div>
                <div className="text-right text-sm">
                  <div className="text-black/50">平均粉丝</div>
                  <div className="text-lg font-bold text-black">
                    {Math.round(insights.avgFollowers / 10000)}万
                  </div>
                </div>
              </div>

              {/* 创作者列表 */}
              <div className="space-y-3">
                {creators.map((creator) => (
                  <div
                    key={creator.id}
                    className="rounded-lg border border-black/10 bg-white p-4 transition-all hover:border-blue-300 hover:shadow-md"
                  >
                    <div className="flex items-start justify-between">
                      <button
                        type="button"
                        className="flex-1 text-left"
                        onClick={() => onSelect(creator.id)}
                      >
                        <div className="flex items-center gap-3">
                          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-lg font-bold text-blue-600">
                            {creator.name.charAt(0)}
                          </div>
                          <div className="flex-1">
                            <h4 className="font-semibold text-black">{creator.name}</h4>
                            <p className="text-xs text-black/50">
                              {Math.round(creator.followers / 10000)}万粉 • {creator.contentForm}
                            </p>
                          </div>
                        </div>
                      </button>
                      <div className="ml-3 text-right">
                        <div className="text-xs text-black/50">互动率</div>
                        <div className="text-sm font-semibold text-green-600">
                          {creator.engagementIndex}%
                        </div>
                      </div>
                    </div>

                    {/* 最近热点 */}
                    <div className="mt-3">
                      <p className="text-xs text-black/50">最近热点</p>
                      <div className="mt-1 flex flex-wrap gap-2">
                        {creator.recentKeywords.map((keyword) => (
                          <span
                            key={keyword}
                            className="rounded-full bg-blue-50 px-3 py-1 text-xs text-blue-700"
                          >
                            #{keyword}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* 赛道洞察 */}
              <div className="mt-4 rounded-lg border-l-4 border-blue-500 bg-blue-50 p-4">
                <h4 className="flex items-center gap-2 font-semibold text-blue-900">
                  <span>💡</span>
                  <span>赛道洞察</span>
                </h4>
                <ul className="mt-3 space-y-2 text-sm text-blue-800">
                  <li className="flex items-start gap-2">
                    <span className="text-blue-400">•</span>
                    <span>{insights.recommendation}</span>
                  </li>
                  {insights.contentGaps.length > 0 && (
                    <>
                      <li className="flex items-start gap-2">
                        <span className="text-blue-400">•</span>
                        <span>
                          <strong>内容空白区: </strong>
                          {insights.contentGaps.join("、")}
                          <span className="ml-2 rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                            竞争少！
                          </span>
                        </span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-blue-400">•</span>
                        <span>
                          <strong>建议定位: </strong>
                          如果你想做{track}，可以主攻"{insights.contentGaps[0]}"方向
                        </span>
                      </li>
                    </>
                  )}
                  {creators.length === 1 && (
                    <li className="flex items-start gap-2">
                      <span className="text-blue-400">•</span>
                      <span>
                        你只关注了1个{track}博主，说明你对这个赛道兴趣不大，或者可以尝试探索更多创作者
                      </span>
                    </li>
                  )}
                  {creators.length >= 2 && (
                    <li className="flex items-start gap-2">
                      <span className="text-blue-400">•</span>
                      <span>
                        这{creators.length}位创作者都在做"
                        {creators[0].recentKeywords[0]}"话题，可以考虑从不同角度切入
                      </span>
                    </li>
                  )}
                </ul>
              </div>
            </div>
          );
        })}
      </div>

      {/* 总结建议 */}
      <div className="mt-6 rounded-xl border-2 border-yellow-200 bg-gradient-to-br from-yellow-50 to-orange-50 p-5">
        <h3 className="flex items-center gap-2 text-lg font-semibold text-yellow-900">
          <span>🎯</span>
          <span>整体建议</span>
        </h3>
        <div className="mt-3 space-y-2 text-sm text-yellow-900">
          <p>
            • <strong>你的关注偏好：</strong>
            主要关注 {Object.keys(clusters).slice(0, 2).join("、")} 赛道
          </p>
          <p>
            • <strong>内容策略：</strong>
            可以尝试跨界组合，比如"{Object.keys(clusters)[0]} + {Object.keys(clusters)[1]}"
          </p>
          <p>
            • <strong>学习路径：</strong>
            先模仿粉丝量较少的创作者（容易上手），再逐步向头部创作者学习
          </p>
        </div>
      </div>
    </section>
  );
}
