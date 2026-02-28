"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { CreatorUniverse } from "@/components/CreatorUniverse";
import type { CreatorNode } from "@/data/creators";

function generateMockEdges(creators: CreatorNode[]) {
  const edges: any[] = [];
  for (let i = 0; i < creators.length; i++) {
    for (let j = i + 1; j < creators.length; j++) {
      const a = creators[i];
      const b = creators[j];
      const same = a.primaryTrack === b.primaryTrack;
      const should = same ? Math.random() > 0.4 : Math.random() > 0.8;
      if (should) {
        edges.push({
          source: a.id,
          target: b.id,
          weight: parseFloat((0.3 + Math.random() * 0.5).toFixed(2)),
          types: { keyword: 0, audience: 0, style: 0 },
        });
      }
    }
  }
  return edges;
}

export function HomePage() {
  const [showScrollTop, setShowScrollTop] = useState(false);
  const [creatorsData, setCreatorsData] = useState<CreatorNode[]>([]);
  const [edgesData, setEdgesData] = useState<any[]>([]);
  const [clustersData, setClustersData] = useState<Record<string, string[]>>({});
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 400);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const r = await fetch('/api/creators');
        if (!mounted) return;

        const contentType = r.headers.get('content-type') || '';
        if (!r.ok) {
          console.warn('Creators API not OK', r.status);
          return;
        }

        if (!contentType.includes('application/json')) {
          const txt = await r.text();
          console.warn('Creators API returned non-json response', txt.slice(0, 500));
          return;
        }

        const json = await r.json();
        console.log('[HomePage] Loaded creators data:', json);
        if (!json) return;

        if (Array.isArray(json.creators)) setCreatorsData(json.creators);
        else setCreatorsData([]);

        if (Array.isArray(json.creatorEdges)) setEdgesData(json.creatorEdges);
        else if (Array.isArray(json.creators)) setEdgesData(generateMockEdges(json.creators));

        if (json.trackClusters && typeof json.trackClusters === 'object') setClustersData(json.trackClusters);
        else setClustersData({});
      } catch (err) {
        console.error('[HomePage] Failed to load creators', err);
      }
    })();
    return () => { mounted = false };
  }, [refreshKey]);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <main className="bg-white">
      {/* Hero 区域 */}
      <section className="relative overflow-hidden pt-20 pb-32 bg-gradient-to-br from-purple-600 via-pink-500 to-purple-600">
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-0 left-0 w-96 h-96 bg-white rounded-full mix-blend-screen"></div>
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-white rounded-full mix-blend-screen"></div>
        </div>

        <div className="relative container mx-auto px-6">
          <div className="max-w-3xl">
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight">
              让创作有迹可循
            </h1>
            <p className="text-lg md:text-xl text-white/85 mb-10 leading-relaxed font-light">
              不再盲目创作。从找到调性相似的标杆，到发现爆品规律，再到智能生成优质文案。三步完成从零到爆款的创作之旅。
            </p>

            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/zh/content-studio" className="inline-flex items-center gap-2 rounded-xl bg-white text-purple-600 px-8 py-4 font-semibold hover:shadow-2xl transition-all text-lg shadow-lg">
                ✨ 立即开始
              </Link>
              <Link href="#features" className="inline-flex items-center gap-2 rounded-xl bg-white/20 backdrop-blur-sm text-white px-8 py-4 font-medium hover:bg-white/30 transition-all border border-white/50">
                了解功能 ↓
              </Link>
            </div>

            {/* 数据展示 */}
            <div className="mt-16 grid grid-cols-3 gap-8">
              <div className="text-center">
                <div className="text-3xl font-bold text-white mb-2">3步</div>
                <div className="text-white/80 text-sm">智能创作流程</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white mb-2">7种</div>
                <div className="text-white/80 text-sm">AI内容模板</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white mb-2">∞</div>
                <div className="text-white/80 text-sm">爆品可能性</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="py-20 bg-white">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-black mb-4">核心功能</h2>
            <p className="text-black/60 text-lg max-w-2xl mx-auto">三步创作流程，让你的内容策略更清晰、更系统、更有效</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="rounded-2xl bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 p-8 hover:shadow-xl transition-shadow">
              <div className="text-4xl mb-4">👤</div>
              <h3 className="text-xl font-bold text-black mb-3">第一步：确认身份</h3>
              <p className="text-black/70 mb-2">选择你的创作者账号，系统会展示你的粉丝数、互动数和内容方向。</p>
              <ul className="text-sm text-black/60 space-y-1">
                <li>✓ 快速选择创作者身份</li>
                <li>✓ 实时展示账号数据</li>
              </ul>
            </div>

            <div className="rounded-2xl bg-gradient-to-br from-purple-50 to-pink-100 border border-pink-200 p-8 hover:shadow-xl transition-shadow">
              <div className="text-4xl mb-4">🔮</div>
              <h3 className="text-xl font-bold text-black mb-3">第二步：发现灵感</h3>
              <p className="text-black/70 mb-2">AI 匹配调性相似博主，深度分析爆款内容，或直接语义搜索全库笔记。</p>
              <ul className="text-sm text-black/60 space-y-1">
                <li>✓ Embedding 向量相似度排序</li>
                <li>✓ 爆品机会分析 + 笔记语义搜索</li>
              </ul>
            </div>

            <div className="rounded-2xl bg-gradient-to-br from-pink-50 to-purple-100 border border-purple-200 p-8 hover:shadow-xl transition-shadow">
              <div className="text-4xl mb-4">✨</div>
              <h3 className="text-xl font-bold text-black mb-3">第三步：生成文案</h3>
              <p className="text-black/70 mb-2">7种AI模板，智能生成优质文案。</p>
              <ul className="text-sm text-black/60 space-y-1">
                <li>✓ 7种专业内容模板</li>
                <li>✓ 一键复制到剪贴板</li>
              </ul>
            </div>
          </div>

          <div className="mt-16 text-center">
            <Link href="/zh/content-studio" className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 text-white px-10 py-4 font-bold text-lg hover:from-purple-700 hover:to-pink-700 transition-all shadow-lg">
              🚀 现在就开始创作
            </Link>
          </div>
        </div>
      </section>

      {/* 创作者网络 */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-black mb-4">创作者网络</h2>
            <p className="text-black/60 text-lg">
              探索数百位创作者的内容生态，发现调性相似的标杆账号
            </p>
          </div>

          <div className="rounded-3xl bg-white p-8 shadow-lg border border-black/5">
            {/* 数据加载状态指示器 */}
            {creatorsData.length === 0 && (
              <div className="text-center py-12">
                <div className="text-gray-400 text-lg">正在加载创作者网络数据...</div>
                <div className="text-sm text-gray-500 mt-2">如果长时间未加载，请检查浏览器控制台</div>
              </div>
            )}
            
            {creatorsData.length > 0 && (
              <div className="text-sm text-gray-600 mb-4">
                已加载 {creatorsData.length} 位创作者，{edgesData.length} 条关系
              </div>
            )}
            
            <CreatorUniverse
              creators={creatorsData}
              edges={edgesData}
              clusters={clustersData}
              trendingKeywords={[]}
              onCreatorAdded={() => setRefreshKey(k => k + 1)}
            />
          </div>
        </div>
      </section>


      {/* 返回顶部按钮 */}
      {showScrollTop && (
        <button
          onClick={scrollToTop}
          className="fixed bottom-8 right-8 z-50 flex h-12 w-12 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg transition-all hover:bg-blue-700 hover:scale-110 active:scale-95"
          aria-label="返回顶部"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="h-6 w-6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 15.75l7.5-7.5 7.5 7.5" />
          </svg>
        </button>
      )}
    </main>
  );
}
