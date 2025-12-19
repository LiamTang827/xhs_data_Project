"use client";

import { useEffect, useRef, useState } from "react";
import { forceSimulation, forceLink, forceManyBody, forceCenter, forceCollide } from "d3-force";
import type { CreatorEdge, CreatorNode } from "@/data/creators";

interface CreatorNetworkGraphProps {
  nodes: CreatorNode[];
  edges: CreatorEdge[];
  activeId?: string;
  onNodeSelect: (id: string) => void;
}

type SimNode = {
  id: string;
  name: string;
  followers: number;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
};

type SimLink = {
  source: SimNode | string;
  target: SimNode | string;
  weight: number;
};

const WIDTH = 800;
const HEIGHT = 640;
const NODE_PADDING = 40;

export function CreatorNetworkGraph({
  nodes,
  edges,
  activeId,
  onNodeSelect,
}: CreatorNetworkGraphProps) {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const simulationRef = useRef<any>(null);
  const [simNodes, setSimNodes] = useState<SimNode[]>([]);
  const [simLinks, setSimLinks] = useState<SimLink[]>([]);
  const [dragNodeId, setDragNodeId] = useState<string | null>(null);
  const dragMovedRef = useRef(false);
  const lastDragTimeRef = useRef<number | null>(null);

  // 计算节点半径
  const getNodeRadius = (followers: number): number => {
    const followerCounts = nodes.map((n) => n.followers);
    const min = Math.min(...followerCounts);
    const max = Math.max(...followerCounts);
    const range = max - min || 1;
    const normalized = (followers - min) / range;
    return 18 + normalized * 18;
  };

  // 初始化模拟
  useEffect(() => {
    // 创建节点（如果 position 为 0,0 则随机分布在中心附近）
    const nodeMap = new Map<string, SimNode>();
    const sNodes: SimNode[] = nodes.map((node) => {
      const hasValidPosition = node.position && (node.position.x !== 0 || node.position.y !== 0);
      const sn: SimNode = {
        id: node.id,
        name: node.name,
        followers: node.followers,
        x: hasValidPosition ? (node.position.x / 100) * WIDTH : WIDTH / 2 + (Math.random() - 0.5) * 200,
        y: hasValidPosition ? (node.position.y / 100) * HEIGHT : HEIGHT / 2 + (Math.random() - 0.5) * 200,
        fx: null,
        fy: null,
      };
      nodeMap.set(node.id, sn);
      return sn;
    });

    // 创建边并记录缺失节点的边用于调试
    const sLinks = edges
      .map((edge) => {
        const source = nodeMap.get(edge.source);
        const target = nodeMap.get(edge.target);
        if (!source || !target) {
          console.warn('[CreatorNetworkGraph] Edge missing node:', edge.source, edge.target);
          return null;
        }
        return {
          source,
          target,
          weight: edge.weight,
        } as SimLink;
      })
      .filter((link): link is SimLink => link !== null);

    console.log('[CreatorNetworkGraph] Created nodes:', sNodes.length, 'Created links:', sLinks.length);
    if (sLinks.length > 0) {
      console.log('[CreatorNetworkGraph] First link:', {
        source: typeof sLinks[0].source === 'string' ? sLinks[0].source : sLinks[0].source.id,
        target: typeof sLinks[0].target === 'string' ? sLinks[0].target : sLinks[0].target.id,
        weight: sLinks[0].weight,
      });
    }

    setSimNodes(sNodes);
    setSimLinks(sLinks);

    // 创建力模拟（调整参数以获得更紧凑的布局）
    const simulation = forceSimulation(sNodes as any)
      .force(
        'link',
        forceLink(sLinks as any)
          .id((d: any) => d.id)
          .distance(80) // 固定边长，避免过度分散
          .strength(0.8) // 增强连边强度
      )
      .force('charge', forceManyBody().strength(-400)) // 增强排斥力
      .force('center', forceCenter(WIDTH / 2, HEIGHT / 2))
      .force('collision', forceCollide((d: any) => getNodeRadius(d.followers) + 15))
      .alphaDecay(0.01)
      .velocityDecay(0.3)
      .on('tick', () => {
        sNodes.forEach((node) => {
          if (typeof node.x === 'number') {
            node.x = Math.max(NODE_PADDING, Math.min(WIDTH - NODE_PADDING, node.x))
          }
          if (typeof node.y === 'number') {
            node.y = Math.max(NODE_PADDING, Math.min(HEIGHT - NODE_PADDING, node.y))
          }
        })
        setSimNodes([...sNodes]);
      });

    simulationRef.current = simulation;

    // 初始化位置 - 多次迭代让布局更稳定
    for (let i = 0; i < 300; i += 1) {
      simulation.tick();
    }
    sNodes.forEach((node) => {
      if (typeof node.x === 'number') {
        node.x = Math.max(NODE_PADDING, Math.min(WIDTH - NODE_PADDING, node.x))
      }
      if (typeof node.y === 'number') {
        node.y = Math.max(NODE_PADDING, Math.min(HEIGHT - NODE_PADDING, node.y))
      }
    })
    setSimNodes([...sNodes]);
    setSimLinks([...sLinks]);

    return () => {
      simulation.stop();
    };
  }, [nodes, edges]);

  // 鼠标事件处理
  const onNodeMouseDown = (e: React.MouseEvent, nodeId: string) => {
    e.preventDefault();
    e.stopPropagation();
    setDragNodeId(nodeId);
    dragMovedRef.current = false;
    lastDragTimeRef.current = Date.now();

    const node = simNodes.find((n) => n.id === nodeId);
    if (node && svgRef.current) {
      const pt = svgRef.current.createSVGPoint();
      pt.x = e.clientX;
      pt.y = e.clientY;
      const svgP = pt.matrixTransform(svgRef.current.getScreenCTM()?.inverse());
      node.fx = svgP.x;
      node.fy = svgP.y;
    }

    // 重新加热模拟
    if (simulationRef.current) {
      simulationRef.current.alpha(0.3).restart();
    }
  };

  const onSvgMouseMove = (e: React.MouseEvent) => {
    if (!dragNodeId || !svgRef.current) return;
    dragMovedRef.current = true;

    const node = simNodes.find((n) => n.id === dragNodeId);
    if (!node) return;

    const pt = svgRef.current.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    const svgP = pt.matrixTransform(svgRef.current.getScreenCTM()?.inverse());
    node.fx = svgP.x;
    node.fy = svgP.y;

    // 重新加热模拟
    if (simulationRef.current) {
      simulationRef.current.alpha(0.5).restart();
    }
  };

  const onSvgMouseUp = () => {
    if (!dragNodeId) return;

    const node = simNodes.find((n) => n.id === dragNodeId);
    if (node) {
      node.fx = null;
      node.fy = null;

      // 让模拟继续运行
      if (simulationRef.current) {
        simulationRef.current.alpha(0.3).restart();
      }
    }

    setDragNodeId(null);
  };

  const onNodeClick = (e: React.MouseEvent, nodeId: string) => {
    e.stopPropagation();
    // 如果刚拖拽过，不触发点击
    if (dragMovedRef.current && lastDragTimeRef.current && Date.now() - lastDragTimeRef.current < 200) {
      dragMovedRef.current = false;
      return;
    }
    onNodeSelect(nodeId);
  };

  // 获取边的源和目标节点
  const getLinkNodes = (link: SimLink) => {
    const source = typeof link.source === "string" ? simNodes.find((n) => n.id === link.source) : link.source;
    const target = typeof link.target === "string" ? simNodes.find((n) => n.id === link.target) : link.target;
    return { source, target };
  };

  return (
    <div className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm">
      <svg
        ref={svgRef}
        width={WIDTH}
        height={HEIGHT}
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        className="cursor-default select-none"
        style={{ width: "100%", height: "auto" }}
        onMouseMove={onSvgMouseMove}
        onMouseUp={onSvgMouseUp}
        onMouseLeave={onSvgMouseUp}
      >
        {/* 绘制边 */}
        <g>
          {simLinks.map((link, idx) => {
            const { source, target } = getLinkNodes(link);
            if (!source || !target || source.x === undefined || target.x === undefined) return null;

            const isHighlighted =
              activeId && (source.id === activeId || target.id === activeId);
            const strokeWidth = 1 + link.weight * 4;
            const opacity = isHighlighted ? 0.8 : 0.3;
            const color = isHighlighted ? "#2563eb" : "#94a3b8";

            return (
              <line
                key={`link-${idx}`}
                x1={source.x}
                y1={source.y!}
                x2={target.x}
                y2={target.y!}
                stroke={color}
                strokeWidth={strokeWidth}
                opacity={opacity}
              />
            );
          })}
        </g>

        {/* 绘制节点 */}
        <g>
          {simNodes.map((node) => {
            if (node.x === undefined || node.y === undefined) return null;

            const radius = getNodeRadius(node.followers);
            const isActive = node.id === activeId;
            const isConnected =
              activeId &&
              simLinks.some((link) => {
                const { source, target } = getLinkNodes(link);
                return (
                  (source?.id === activeId && target?.id === node.id) ||
                  (target?.id === activeId && source?.id === node.id)
                );
              });

            const fill = isActive ? "#1d4ed8" : isConnected ? "#2563eb" : "#60a5fa";
            const isDragging = dragNodeId === node.id;

            return (
              <g
                key={`node-${node.id}`}
                transform={`translate(${node.x}, ${node.y})`}
                onMouseDown={(e) => onNodeMouseDown(e, node.id)}
                onClick={(e) => onNodeClick(e, node.id)}
                style={{ cursor: isDragging ? "grabbing" : "grab" }}
              >
                <circle
                  r={radius}
                  fill={fill}
                  stroke="white"
                  strokeWidth={2}
                  style={{
                    filter: isActive ? "drop-shadow(0 0 8px rgba(29, 78, 184, 0.6))" : undefined,
                  }}
                />
                <text
                  x={0}
                  y={radius + 16}
                  textAnchor="middle"
                  fontSize={12}
                  fill="#111827"
                  style={{ pointerEvents: "none", userSelect: "none" }}
                >
                  {node.name}
                </text>
              </g>
            );
          })}
        </g>
      </svg>
    </div>
  );
}
