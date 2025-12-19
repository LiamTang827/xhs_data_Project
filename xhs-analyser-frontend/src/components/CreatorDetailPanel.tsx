"use client";

import { useState, useMemo } from "react";
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
      <LineChart series={series} />
    </div>
  );
}

export function CreatorDetailPanel({ node }: CreatorDetailPanelProps) {
  const [showFullProfile, setShowFullProfile] = useState(false);

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

      {/* 统计数据和 Creator Index 图 */}
      <dl className="mt-6 grid grid-cols-2 gap-4 text-sm">
        <div>
          <dt className="text-black/50">粉丝数</dt>
          <dd className="text-lg font-semibold text-black">
            {node.followers.toLocaleString()}
          </dd>
        </div>
        <div>
          <dt className="text-black/50">互动率</dt>
          <dd className="text-lg font-semibold text-black">{node.engagementIndex}%</dd>
        </div>
      </dl>

      {/* Creator Index 折线图 - 直接显示 */}
      <div className="mt-6">
        <IndexChartPanel node={node} />
      </div>

      {/* 标签 */}
      {node.recentKeywords && node.recentKeywords.length > 0 && (
        <div className="mt-6">
          <h4 className="text-sm font-semibold text-black/70">标签</h4>
          <div className="mt-2 flex flex-wrap gap-2">
            {node.recentKeywords.map((keyword) => (
              <span
                key={`${node.id}-${keyword}`}
                className="rounded-full bg-blue-50 px-3 py-1 text-xs text-blue-700"
              >
                #{keyword}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* 完整画像折叠内容 */}
      {showFullProfile && (
        <div className="mt-6 border-t border-black/10 pt-6">
          <h4 className="text-sm font-semibold text-black/70 mb-3">完整画像</h4>

          {/* 其余元信息 */}
          {node.desc && (
            <div className="mb-4">
              <dt className="text-xs text-black/50 mb-1">个人简介</dt>
              <dd className="text-sm text-black/80 whitespace-pre-wrap leading-relaxed">
                {node.desc}
              </dd>
            </div>
          )}

          {node.redId && (
            <div className="mb-4">
              <dt className="text-xs text-black/50 mb-1">小红书号</dt>
              <dd className="text-sm text-black/80 font-mono">
                {node.redId}
              </dd>
            </div>
          )}

          <div className="mb-4">
            <dt className="text-xs text-black/50 mb-1">用户 ID</dt>
            <dd className="text-sm text-black/80 font-mono break-all">
              {node.id}
            </dd>
          </div>

          {node.avatar && (
            <div>
              <dt className="text-xs text-black/50 mb-1">头像</dt>
              <dd className="text-xs text-blue-600 break-all hover:underline">
                <a href={node.avatar} target="_blank" rel="noopener noreferrer">
                  查看原图 →
                </a>
              </dd>
            </div>
          )}
        </div>
      )}

      {/* 查看完整画像按钮 */}
      <button
        onClick={() => setShowFullProfile(!showFullProfile)}
        className="mt-6 w-full text-sm text-blue-600 hover:text-blue-700 transition-colors flex items-center justify-center gap-1"
      >
        {showFullProfile ? '收起' : '查看完整画像'}
        <span className={`transition-transform ${showFullProfile ? 'rotate-180' : ''}`}>
          ↓
        </span>
      </button>
    </div>
  );
}
