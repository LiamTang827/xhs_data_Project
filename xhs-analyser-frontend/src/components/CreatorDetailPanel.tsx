"use client";

import { useMemo } from "react";
import type { CreatorNode } from "@/data/creators";

interface CreatorDetailPanelProps {
  node?: CreatorNode;
}

type SeriesPoint = { ts: number; value: number };

function LineChart({ series, height = 200 }: { series: SeriesPoint[]; height?: number }) {
  const padding = { left: 40, right: 16, top: 12, bottom: 28 };
  const width = 560;
  const innerW = width - padding.left - padding.right;
  const innerH = height - padding.top - padding.bottom;

  if (!series || series.length === 0) {
    return (
      <div className="flex h-40 items-center justify-center text-sm text-black/50">无时间序列数据</div>
    );
  }

  const sorted = [...series].sort((a, b) => a.ts - b.ts);
  const xs = sorted.map((d) => d.ts);
  const ys = sorted.map((d) => d.value);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys, 0);
  const maxY = Math.max(...ys, 1);

  const xScale = (t: number) => {
    if (maxX === minX) return padding.left + innerW / 2;
    return padding.left + ((t - minX) / (maxX - minX)) * innerW;
  };
  const yScale = (v: number) => {
    if (maxY === minY) return padding.top + innerH / 2;
    // invert y
    return padding.top + innerH - ((v - minY) / (maxY - minY)) * innerH;
  };

  const points = sorted.map((d) => `${xScale(d.ts)},${yScale(d.value)}`).join(" ");

  // x labels: up to 4 labels
  const labelCount = Math.min(4, sorted.length);
  const labelIndexes = Array.from({ length: labelCount }, (_, i) => Math.floor((i * (sorted.length - 1)) / (labelCount - 1 || 1)));

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full" preserveAspectRatio="xMidYMid meet">
      {/* grid horizontal lines */}
      {[0, 0.25, 0.5, 0.75, 1].map((p) => (
        <line
          key={p}
          x1={padding.left}
          x2={width - padding.right}
          y1={padding.top + p * innerH}
          y2={padding.top + p * innerH}
          stroke="#eee"
          strokeWidth={1}
        />
      ))}

      {/* polyline */}
      <polyline fill="none" stroke="#2563eb" strokeWidth={2} points={points} strokeLinecap="round" strokeLinejoin="round" />

      {/* points */}
      {sorted.map((d, i) => (
        <g key={i}>
          <circle cx={xScale(d.ts)} cy={yScale(d.value)} r={4} fill="#fff" stroke="#2563eb" strokeWidth={2} />
        </g>
      ))}

      {/* x labels */}
      {labelIndexes.map((li, idx) => {
        const d = sorted[li];
        const x = xScale(d.ts);
        const label = new Date(d.ts).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
        return (
          <text key={idx} x={x} y={height - 6} fontSize={11} textAnchor="middle" fill="#666">
            {label}
          </text>
        );
      })}

      {/* y axis labels: min and max */}
      <text x={8} y={padding.top + innerH} fontSize={11} fill="#666">{minY}</text>
      <text x={8} y={padding.top + 10} fontSize={11} fill="#666">{maxY}</text>
    </svg>
  );
}

function IndexChartPanel({ node }: { node?: CreatorNode }) {
  // Determine series data from node.indexSeries (Array<{ts:number,value:number}>)
  const series = useMemo(() => {
    if (!node) {
      console.log('[IndexChart] No node');
      return [] as SeriesPoint[];
    }
    
    // @ts-ignore
    const indexSeries = node.indexSeries;
    console.log('[IndexChart] node:', node.name, 'indexSeries:', indexSeries);
    
    if (Array.isArray(indexSeries) && indexSeries.length > 0) {
      const result = indexSeries
        .map((p: any) => {
          const ts = Number(p.ts);
          const value = Number(p.value);
          if (!Number.isNaN(ts) && !Number.isNaN(value)) {
            return { ts, value };
          }
          return null;
        })
        .filter((p): p is SeriesPoint => p !== null);
      console.log('[IndexChart] Parsed series:', result);
      return result;
    }

    console.log('[IndexChart] No valid indexSeries found');
    return [] as SeriesPoint[];
  }, [node]);

  return (
    <div className="rounded-lg bg-white p-4 border border-black/5 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <div className="text-sm font-medium text-black/70">Creator Index</div>
        <div className="text-xs text-black/40">基于发布数据的影响力指数</div>
      </div>
      <LineChart series={series} height={280} />
    </div>
  );
}

export function CreatorDetailPanel({ node }: CreatorDetailPanelProps) {
  if (!node) {
    return (
      <div className="flex h-full items-center justify-center rounded-2xl border border-dashed border-black/20 bg-white/70 p-8 text-sm text-black/50">
        点击网络图中的创作者节点查看详情
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm">
      {/* 头部 - 头像和基本信息 */}
      <div className="flex items-start gap-4">
        {node.avatar && (
          <img 
            src={node.avatar} 
            alt={node.name}
            className="h-16 w-16 rounded-full object-cover border-2 border-blue-100"
          />
        )}
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-semibold text-black">{node.name}</h3>
            <span className="rounded-full bg-black/10 px-3 py-1 text-xs uppercase tracking-wide text-black/60">
              {node.primaryTrack}
            </span>
          </div>
          {node.ipLocation && (
            <p className="mt-1 text-sm text-black/50">📍 {node.ipLocation}</p>
          )}
        </div>
      </div>

      {/* 统计数据 - 更大更醒目的显示 */}
      <div className="mt-6 rounded-xl bg-gradient-to-br from-blue-50 to-indigo-50 p-6">
        <div className="grid grid-cols-2 gap-6">
          {/* 粉丝规模 */}
          <div className="text-center">
            <dt className="text-sm font-medium text-black/60 mb-2">📊 粉丝规模</dt>
            <dd className="text-1xl font-bold text-black tracking-tight">
              {node.followers.toLocaleString()}
            </dd>
            {/* 7天增长 */}
            {node.fansGrowth7d !== undefined && node.fansGrowth7d !== null && (
              <div className={`mt-2 inline-flex items-center gap-1 rounded-full px-3 py-1.5 text-sm font-semibold ${
                node.fansGrowth7d > 0 ? 'bg-green-100 text-green-700' : 
                node.fansGrowth7d < 0 ? 'bg-red-100 text-red-700' : 
                'bg-gray-100 text-gray-700'
              }`}>
                <span className="text-lg">{node.fansGrowth7d > 0 ? '↗' : node.fansGrowth7d < 0 ? '↘' : '→'}</span>
                <span>7天 {node.fansGrowth7d > 0 ? '+' : ''}{node.fansGrowth7d.toLocaleString()}</span>
                {node.followers > 0 && (
                  <span className="text-xs opacity-75">
                    ({((node.fansGrowth7d / node.followers) * 100).toFixed(2)}%)
                  </span>
                )}
              </div>
            )}
          </div>
          
          {/* 30天互动 */}
          <div className="text-center">
            <dt className="text-sm font-medium text-black/60 mb-2">🔥 30天互动</dt>
            <dd className="text-2xl font-bold text-indigo-600 tracking-tight">
              {node.totalEngagement?.toLocaleString() || 0}
            </dd>
            <div className="mt-2 text-xs text-black/50">
              {node.noteCount || 0}篇笔记 · 平均{node.noteCount ? Math.round((node.totalEngagement || 0) / node.noteCount).toLocaleString() : 0}互动/篇
            </div>
          </div>
        </div>
      </div>

      {/* Creator Index 折线图 - 直接显示 */}
      <div className="mt-6">
        <IndexChartPanel node={node} />
      </div>

      {/* 流量密码 - 基于该创作者的热门话题 */}
      {((node.topics && node.topics.length > 0) || (node.recentKeywords && node.recentKeywords.length > 0)) && (
        <div className="mt-6">
          <div className="mb-3 flex items-center gap-2">
            <h4 className="text-sm font-semibold text-black/70">🔥 流量密码</h4>
            <span className="text-xs text-black/40">·</span>
            <span className="text-xs text-black/40">基于最近笔记热门话题</span>
          </div>
          <div className="rounded-xl border border-blue-100 bg-gradient-to-br from-blue-50/50 to-purple-50/50 p-4">
            <div className="flex flex-wrap gap-2">
              {(node.topics || node.recentKeywords || []).slice(0, 8).map((topic, idx) => (
                <button
                  key={`${node.id}-topic-${idx}`}
                  onClick={() => {
                    navigator.clipboard.writeText(topic);
                    // 可以添加toast提示
                  }}
                  className="group rounded-lg border border-blue-200 bg-white px-3 py-2 text-sm text-black/80 hover:border-blue-400 hover:bg-blue-50 hover:text-blue-700 transition-all hover:scale-105 active:scale-95 cursor-pointer"
                  title="点击复制话题"
                >
                  <span className="font-medium">#{topic}</span>
                  <span className="ml-1.5 opacity-0 group-hover:opacity-100 transition-opacity">📋</span>
                </button>
              ))}
            </div>
            <div className="mt-3 pt-3 border-t border-blue-100">
              <p className="text-xs text-black/60 leading-relaxed">
                💡 <strong>使用提示：</strong>点击话题复制后，前往 AI风格生成器 粘贴生成内容
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
