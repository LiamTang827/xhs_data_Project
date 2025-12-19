"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ReactNode } from "react";

interface TrendingTopic {
  topic: string;
  heatScore: number;
  creators: string[];
  avgViews: string;
  growthRate: string;
  competitionLevel: "低" | "中" | "高";
  suggestedAngles: string[];
}

interface TrendingTopicsProps {
  data: TrendingTopic[];
  renderCreatorTag?: (creatorId: string) => ReactNode;
}

const getCompetitionColor = (level: "低" | "中" | "高") => {
  switch (level) {
    case "低":
      return "text-green-600 bg-green-50";
    case "中":
      return "text-yellow-600 bg-yellow-50";
    case "高":
      return "text-red-600 bg-red-50";
  }
};

const getHeatEmoji = (score: number) => {
  if (score >= 80) return "🔥🔥🔥🔥🔥";
  if (score >= 60) return "🔥🔥🔥🔥";
  if (score >= 40) return "🔥🔥🔥";
  if (score >= 20) return "🔥🔥";
  return "🔥";
};

export function TrendingTopics({ data, renderCreatorTag }: TrendingTopicsProps) {
  return (
    <div
      id="trending"
      className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm"
    >
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-black">🔥 流量密码榜</h2>
        <p className="mt-2 text-sm text-black/60">
          分析你关注的创作者正在做的热点内容，帮你快人一步抓住流量
        </p>
        <span className="mt-1 inline-block rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-600">
          近 7 天数据
        </span>
      </div>

      <div className="grid gap-6 lg:grid-cols-[2fr_3fr]">
        {/* 左侧：热度排行图 */}
        <div className="h-80 w-full min-h-[320px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis type="number" hide domain={[0, 100]} />
              <YAxis dataKey="topic" type="category" width={100} fontSize={12} />
              <Tooltip
                cursor={{ fill: "rgba(37, 99, 235, 0.08)" }}
                contentStyle={{ borderRadius: 12, border: "1px solid #e5e7eb" }}
                content={({ active, payload }) => {
                  if (!active || !payload?.[0]) return null;
                  const item = payload[0].payload as TrendingTopic;
                  return (
                    <div className="rounded-xl border border-black/10 bg-white p-3 shadow-lg">
                      <p className="font-semibold text-black">{item.topic}</p>
                      <p className="text-sm text-black/60">热度: {item.heatScore}</p>
                      <p className="text-sm text-black/60">增长: {item.growthRate}</p>
                    </div>
                  );
                }}
              />
              <Bar dataKey="heatScore" fill="#2563eb" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 右侧：详细分析 */}
        <div className="space-y-4">
          {data?.map((item, index) => (
            <div
              key={item.topic}
              className="rounded-xl border border-black/10 bg-gradient-to-br from-white to-gray-50 p-4 transition-all hover:shadow-md"
            >
              {/* 标题行 */}
              <div className="flex items-start justify-between">
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
