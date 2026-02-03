"use client";

import { useEffect, useState, useMemo } from "react";
import type { ReactNode } from "react";
import type { CreatorNode } from "@/data/creators";

interface TopicWithCount {
  topic: string;
  count: number;
  creators: string[];
}

interface TrendingTopicsProps {
  creators: CreatorNode[];
  clusters: Record<string, string[]>;
  renderCreatorTag?: (creatorId: string) => ReactNode;
}

export function TrendingTopics({ creators, clusters, renderCreatorTag }: TrendingTopicsProps) {
  const [hotTopics, setHotTopics] = useState<TopicWithCount[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // 计算热门话题
  const calculateHotTopics = useMemo(() => {
    const topicMap = new Map<string, Set<string>>();
    
    // 遍历所有创作者，提取话题
    creators.forEach(creator => {
      const topics = creator.topics || [];
      topics.forEach(topic => {
        if (!topicMap.has(topic)) {
          topicMap.set(topic, new Set());
        }
        topicMap.get(topic)?.add(creator.name);
      });
    });

    // 转换为数组并排序
    const topicsArray: TopicWithCount[] = Array.from(topicMap.entries()).map(([topic, creatorSet]) => ({
      topic,
      count: creatorSet.size,
      creators: Array.from(creatorSet),
    }));

    // 按出现次数排序
    return topicsArray.sort((a, b) => b.count - a.count).slice(0, 15);
  }, [creators]);

  useEffect(() => {
    setHotTopics(calculateHotTopics);
    setIsLoading(false);
  }, [calculateHotTopics]);

  // 获取热度emoji
  const getHeatEmoji = (count: number, maxCount: number) => {
    const percentage = (count / maxCount) * 100;
    if (percentage >= 80) return "🔥🔥🔥🔥🔥";
    if (percentage >= 60) return "🔥🔥🔥🔥";
    if (percentage >= 40) return "🔥🔥🔥";
    if (percentage >= 20) return "🔥🔥";
    return "🔥";
  };

  const maxCount = hotTopics[0]?.count || 1;

  return (
    <div
      id="traffic-secrets"
      className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm"
    >
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-black flex items-center gap-2">
          🔥 流量密码
          <span className="text-lg text-black/40">·</span>
          <span className="text-lg font-normal text-black/60">基于你关注的创作者圈</span>
        </h2>
        <p className="mt-2 text-sm text-black/60">
          这些是你关注的创作者们正在讨论的热门话题，可以直接用于AI风格生成器
        </p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-40">
          <div className="text-black/40">正在分析...</div>
        </div>
      ) : hotTopics.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-40 text-center">
          <div className="text-4xl mb-2">📊</div>
          <div className="text-black/60">暂无话题数据</div>
          <div className="text-sm text-black/40 mt-1">添加更多创作者后，这里会显示热门话题</div>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {hotTopics.map((item, index) => (
            <div
              key={item.topic}
              className="group rounded-xl border border-black/10 bg-gradient-to-br from-white to-blue-50/30 p-4 transition-all hover:shadow-lg hover:scale-105 cursor-pointer"
            >
              {/* 排名和热度 */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-600">
                    {index + 1}
                  </span>
                  <span className="text-lg">
                    {getHeatEmoji(item.count, maxCount)}
                  </span>
                </div>
                <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-600">
                  {item.count}位创作者
                </span>
              </div>

              {/* 话题名称 */}
              <h3 className="text-base font-semibold text-black mb-3 line-clamp-2 group-hover:text-blue-600 transition-colors">
                {item.topic}
              </h3>

              {/* 创作者标签 */}
              <div className="flex flex-wrap gap-1.5">
                {item.creators.slice(0, 3).map(creatorName => (
                  <span
                    key={creatorName}
                    className="inline-flex items-center rounded-full bg-white border border-black/10 px-2 py-0.5 text-xs text-black/70"
                  >
                    {renderCreatorTag?.(creatorName) || creatorName}
                  </span>
                ))}
                {item.creators.length > 3 && (
                  <span className="inline-flex items-center rounded-full bg-black/5 px-2 py-0.5 text-xs text-black/50">
                    +{item.creators.length - 3}
                  </span>
                )}
              </div>

              {/* 操作提示 */}
              <div className="mt-3 pt-3 border-t border-black/5">
                <button
                  onClick={() => {
                    // 复制话题到剪贴板
                    navigator.clipboard.writeText(item.topic);
                    // 可以添加提示
                  }}
                  className="text-xs text-blue-600 hover:text-blue-700 font-medium transition-colors"
                >
                  📋 复制话题用于生成
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 使用提示 */}
      {hotTopics.length > 0 && (
        <div className="mt-6 rounded-xl bg-blue-50 border border-blue-100 p-4">
          <div className="flex items-start gap-3">
            <div className="text-2xl">💡</div>
            <div className="flex-1">
              <h4 className="font-semibold text-black mb-1">如何使用流量密码</h4>
              <p className="text-sm text-black/70 leading-relaxed">
                1. 点击"📋 复制话题"按钮，将热门话题复制到剪贴板<br/>
                2. 前往 AI风格生成器，粘贴话题到输入框<br/>
                3. 选择一位创作者风格，生成符合当前热点的内容<br/>
                4. 这些话题都是你关注圈内正在讨论的，更容易获得流量
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-600">
                      {index + 1}
                    </span>
                    <h3 className="text-lg font-semibold text-black">{item.topic}</h3>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-black/50">热度</div>
                  <div className="text-sm font-semibold text-black">
                    {getHeatEmoji(item.heatScore)} {item.heatScore}
                  </div>
                </div>
              </div>

              {/* 数据指标 */}
              <div className="mt-3 flex gap-4 text-sm">
                <div className="flex items-center gap-1">
                  <span className="text-black/50">竞争:</span>
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${getCompetitionColor(item.competitionLevel)}`}
                  >
                    {item.competitionLevel}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="text-black/50">增长:</span>
                  <span className="font-medium text-green-600">{item.growthRate}</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="text-black/50">平均播放:</span>
                  <span className="font-medium text-black">{item.avgViews}</span>
                </div>
              </div>

              {/* 建议切入角度 */}
              {item.suggestedAngles.length > 0 && (
                <div className="mt-3 rounded-lg bg-blue-50 p-3">
                  <p className="text-xs font-semibold text-blue-900">✨ 建议切入角度</p>
                  <ul className="mt-2 space-y-1">
                    {item.suggestedAngles.map((angle, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm text-blue-800">
                        <span className="text-blue-400">•</span>
                        <span>
                          {angle}
                          {idx === 0 && item.competitionLevel === "低" && (
                            <span className="ml-2 rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                              竞争少！
                            </span>
                          )}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* 正在做的创作者 */}
              <div className="mt-3">
                <p className="text-xs text-black/50">👥 正在做的大V</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {item.creators.map((creatorId) => (
                    <span
                      key={`${item.topic}-${creatorId}`}
                      className="rounded-full bg-black/5 px-3 py-1 text-xs text-black/70 transition-colors hover:bg-black/10"
                    >
                      {renderCreatorTag ? renderCreatorTag(creatorId) : creatorId}
                    </span>
                  ))}
                </div>
              </div>

              {/* 行动建议 */}
              {item.competitionLevel === "低" && (
                <div className="mt-3 rounded-lg border-l-4 border-green-500 bg-green-50 p-3">
                  <p className="text-sm font-medium text-green-900">
                    💡 这个话题竞争度低，正是入场好时机！
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
