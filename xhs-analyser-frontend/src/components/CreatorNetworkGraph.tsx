"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import {
  forceSimulation,
  forceLink,
  forceManyBody,
  forceCenter,
  forceCollide,
} from "d3-force";
import type { CreatorEdge, CreatorNode } from "@/data/creators";

interface CreatorNetworkGraphProps {
  nodes: CreatorNode[];
  edges: CreatorEdge[];
  activeId?: string;
  onNodeSelect: (id: string) => void;
  /** Compact mode: smaller height for side-by-side layout */
  compact?: boolean;
}

type SimNode = {
  id: string;
  name: string;
  engagement: number;
  avatar?: string;
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

const COLORS = {
  nodeFill: "#818cf8",
  nodeActive: "#6366f1",
  nodeConnected: "#a78bfa",
  nodeStroke: "#ffffff",
  labelColor: "#374151",
};

export function CreatorNetworkGraph({
  nodes,
  edges,
  activeId,
  onNodeSelect,
  compact = false,
}: CreatorNetworkGraphProps) {
  const WIDTH = 800;
  const HEIGHT = compact ? 520 : 640;
  const NODE_PADDING = 44;

  const svgRef = useRef<SVGSVGElement | null>(null);
  const simulationRef = useRef<any>(null);
  const [simNodes, setSimNodes] = useState<SimNode[]>([]);
  const [simLinks, setSimLinks] = useState<SimLink[]>([]);
  const [dragNodeId, setDragNodeId] = useState<string | null>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const dragMovedRef = useRef(false);
  const lastDragTimeRef = useRef<number | null>(null);

  const getNodeRadius = useCallback(
    (engagement: number): number => {
      const values = nodes.map(
        (n) => n.totalEngagement || n.engagementIndex || 0
      );
      const min = Math.min(...values);
      const max = Math.max(...values);
      const range = max - min || 1;
      const normalized = (engagement - min) / range;
      return 20 + normalized * 16;
    },
    [nodes]
  );

  useEffect(() => {
    const nodeMap = new Map<string, SimNode>();
    const sNodes: SimNode[] = nodes.map((node) => {
      const hasPos =
        node.position && (node.position.x !== 0 || node.position.y !== 0);
      const sn: SimNode = {
        id: node.id,
        name: node.name,
        engagement: node.totalEngagement || node.engagementIndex || 0,
        avatar: node.avatar,
        x: hasPos
          ? (node.position.x / 100) * WIDTH
          : WIDTH / 2 + (Math.random() - 0.5) * 200,
        y: hasPos
          ? (node.position.y / 100) * HEIGHT
          : HEIGHT / 2 + (Math.random() - 0.5) * 200,
        fx: null,
        fy: null,
      };
      nodeMap.set(node.id, sn);
      return sn;
    });

    const sLinks = edges
      .map((edge) => {
        const source = nodeMap.get(edge.source);
        const target = nodeMap.get(edge.target);
        if (!source || !target) return null;
        return { source, target, weight: edge.weight } as SimLink;
      })
      .filter((l): l is SimLink => l !== null);

    setSimNodes(sNodes);
    setSimLinks(sLinks);

    const simulation = forceSimulation(sNodes as any)
      .force(
        "link",
        forceLink(sLinks as any)
          .id((d: any) => d.id)
          .distance(90)
          .strength(0.7)
      )
      .force("charge", forceManyBody().strength(-350))
      .force("center", forceCenter(WIDTH / 2, HEIGHT / 2))
      .force(
        "collision",
        forceCollide((d: any) => getNodeRadius(d.engagement) + 14)
      )
      .alphaDecay(0.012)
      .velocityDecay(0.3)
      .on("tick", () => {
        sNodes.forEach((n) => {
          if (typeof n.x === "number")
            n.x = Math.max(NODE_PADDING, Math.min(WIDTH - NODE_PADDING, n.x));
          if (typeof n.y === "number")
            n.y = Math.max(NODE_PADDING, Math.min(HEIGHT - NODE_PADDING, n.y));
        });
        setSimNodes([...sNodes]);
      });

    simulationRef.current = simulation;

    for (let i = 0; i < 300; i++) simulation.tick();
    sNodes.forEach((n) => {
      if (typeof n.x === "number")
        n.x = Math.max(NODE_PADDING, Math.min(WIDTH - NODE_PADDING, n.x));
      if (typeof n.y === "number")
        n.y = Math.max(NODE_PADDING, Math.min(HEIGHT - NODE_PADDING, n.y));
    });
    setSimNodes([...sNodes]);
    setSimLinks([...sLinks]);

    return () => {
      simulation.stop();
    };
  }, [nodes, edges, getNodeRadius, WIDTH, HEIGHT]);

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
    simulationRef.current?.alpha(0.3).restart();
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
    simulationRef.current?.alpha(0.5).restart();
  };

  const onSvgMouseUp = () => {
    if (!dragNodeId) return;
    const node = simNodes.find((n) => n.id === dragNodeId);
    if (node) {
      node.fx = null;
      node.fy = null;
      simulationRef.current?.alpha(0.3).restart();
    }
    setDragNodeId(null);
  };

  const onNodeClick = (e: React.MouseEvent, nodeId: string) => {
    e.stopPropagation();
    if (
      dragMovedRef.current &&
      lastDragTimeRef.current &&
      Date.now() - lastDragTimeRef.current < 200
    ) {
      dragMovedRef.current = false;
      return;
    }
    onNodeSelect(nodeId);
  };

  const getLinkNodes = (link: SimLink) => {
    const source =
      typeof link.source === "string"
        ? simNodes.find((n) => n.id === link.source)
        : link.source;
    const target =
      typeof link.target === "string"
        ? simNodes.find((n) => n.id === link.target)
        : link.target;
    return { source, target };
  };

  const edgePath = (sx: number, sy: number, tx: number, ty: number) => {
    const dx = tx - sx;
    const dy = ty - sy;
    const dr = Math.sqrt(dx * dx + dy * dy) * 1.2;
    return `M${sx},${sy}A${dr},${dr} 0 0,1 ${tx},${ty}`;
  };

  return (
    <svg
      ref={svgRef}
      width={WIDTH}
      height={HEIGHT}
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      className="cursor-default select-none rounded-xl"
      style={{
        width: "100%",
        height: "auto",
        background:
          "linear-gradient(135deg, #f5f3ff 0%, #ede9fe 50%, #f0f9ff 100%)",
      }}
      onMouseMove={onSvgMouseMove}
      onMouseUp={onSvgMouseUp}
      onMouseLeave={onSvgMouseUp}
    >
      <defs>
        <filter id="glow-active" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="4" result="blur" />
          <feFlood floodColor="#818cf8" floodOpacity="0.6" result="color" />
          <feComposite in="color" in2="blur" operator="in" result="shadow" />
          <feMerge>
            <feMergeNode in="shadow" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <filter id="node-shadow" x="-30%" y="-30%" width="160%" height="160%">
          <feDropShadow
            dx="0"
            dy="2"
            stdDeviation="3"
            floodColor="#6366f1"
            floodOpacity="0.25"
          />
        </filter>
        <filter id="glow-hover" x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feFlood floodColor="#a78bfa" floodOpacity="0.4" result="color" />
          <feComposite in="color" in2="blur" operator="in" result="shadow" />
          <feMerge>
            <feMergeNode in="shadow" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <linearGradient
          id="edge-gradient"
          x1="0%"
          y1="0%"
          x2="100%"
          y2="0%"
        >
          <stop offset="0%" stopColor="#c7d2fe" stopOpacity="0.6" />
          <stop offset="100%" stopColor="#ddd6fe" stopOpacity="0.6" />
        </linearGradient>
        <linearGradient
          id="edge-active-gradient"
          x1="0%"
          y1="0%"
          x2="100%"
          y2="0%"
        >
          <stop offset="0%" stopColor="#818cf8" stopOpacity="0.8" />
          <stop offset="100%" stopColor="#a78bfa" stopOpacity="0.8" />
        </linearGradient>
      </defs>

      {/* Dot grid background */}
      <g opacity="0.12">
        {Array.from({ length: Math.floor(WIDTH / 40) }, (_, i) =>
          Array.from({ length: Math.floor(HEIGHT / 40) }, (_, j) => (
            <circle
              key={`dot-${i}-${j}`}
              cx={20 + i * 40}
              cy={20 + j * 40}
              r={1}
              fill="#6366f1"
            />
          ))
        )}
      </g>

      {/* Edges */}
      <g>
        {simLinks.map((link, idx) => {
          const { source, target } = getLinkNodes(link);
          if (
            !source ||
            !target ||
            source.x === undefined ||
            target.x === undefined
          )
            return null;
          const isHighlighted =
            activeId && (source.id === activeId || target.id === activeId);
          const strokeWidth = isHighlighted
            ? 2 + link.weight * 3
            : 1 + link.weight * 2;
          return (
            <path
              key={`link-${idx}`}
              d={edgePath(source.x!, source.y!, target.x!, target.y!)}
              fill="none"
              stroke={
                isHighlighted
                  ? "url(#edge-active-gradient)"
                  : "url(#edge-gradient)"
              }
              strokeWidth={strokeWidth}
              opacity={isHighlighted ? 1 : 0.5}
              style={{ transition: "opacity 0.3s, stroke-width 0.3s" }}
            />
          );
        })}
      </g>

      {/* Nodes */}
      <g>
        {simNodes.map((node) => {
          if (node.x === undefined || node.y === undefined) return null;
          const radius = getNodeRadius(node.engagement);
          const isActive = node.id === activeId;
          const isHovered = node.id === hoveredNodeId;
          const isConnected =
            activeId &&
            simLinks.some((link) => {
              const { source, target } = getLinkNodes(link);
              return (
                (source?.id === activeId && target?.id === node.id) ||
                (target?.id === activeId && source?.id === node.id)
              );
            });
          const isDragging = dragNodeId === node.id;

          let fill = COLORS.nodeFill;
          if (isActive) fill = COLORS.nodeActive;
          else if (isConnected) fill = COLORS.nodeConnected;

          let filter: string | undefined;
          if (isActive) filter = "url(#glow-active)";
          else if (isHovered) filter = "url(#glow-hover)";
          else filter = "url(#node-shadow)";

          const displayName =
            node.name.length > 6 ? node.name.slice(0, 6) + "\u2026" : node.name;

          return (
            <g
              key={`node-${node.id}`}
              transform={`translate(${node.x}, ${node.y})`}
              onMouseDown={(e) => onNodeMouseDown(e, node.id)}
              onClick={(e) => onNodeClick(e, node.id)}
              onMouseEnter={() => setHoveredNodeId(node.id)}
              onMouseLeave={() => setHoveredNodeId(null)}
              style={{
                cursor: isDragging ? "grabbing" : "pointer",
              }}
            >
              <circle
                r={isActive || isHovered ? radius + 2 : radius}
                fill={fill}
                stroke={COLORS.nodeStroke}
                strokeWidth={isActive ? 3 : 2}
                filter={filter}
                style={{ transition: "r 0.2s, fill 0.2s" }}
              />
              {isActive && (
                <circle
                  r={radius + 6}
                  fill="none"
                  stroke="#818cf8"
                  strokeWidth={2}
                  strokeDasharray="4 3"
                  opacity={0.5}
                >
                  <animateTransform
                    attributeName="transform"
                    type="rotate"
                    from="0"
                    to="360"
                    dur="8s"
                    repeatCount="indefinite"
                  />
                </circle>
              )}
              <text
                x={0}
                y={radius + 18}
                textAnchor="middle"
                fontSize={11}
                fontWeight={isActive ? 600 : 500}
                fill={isActive ? "#4f46e5" : COLORS.labelColor}
                style={{ pointerEvents: "none", userSelect: "none" }}
              >
                {displayName}
              </text>
            </g>
          );
        })}
      </g>
    </svg>
  );
}
