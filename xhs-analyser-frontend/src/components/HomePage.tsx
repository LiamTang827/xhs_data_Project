"use client";

import { useState, useEffect } from "react";
import { useTranslations } from "next-intl";
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
  const t = useTranslations("home");
  const [showScrollTop, setShowScrollTop] = useState(false);
  const [creatorsData, setCreatorsData] = useState<CreatorNode[]>([]);
  const [edgesData, setEdgesData] = useState<any[]>([]);
  const [clustersData, setClustersData] = useState<Record<string, string[]>>({});

  useEffect(() => {
    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 400);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    // fetch creators from API route (defensive: handle non-JSON or error HTML responses)
    let mounted = true;
    (async () => {
      try {
        // Use Next.js API route instead of external FastAPI
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

          // prefer server-provided shapes; fall back to local generation
          if (Array.isArray(json.creators)) setCreatorsData(json.creators);
          else setCreatorsData([]);

          if (Array.isArray(json.creatorEdges)) setEdgesData(json.creatorEdges);
          else if (Array.isArray(json.creators)) setEdgesData(generateMockEdges(json.creators));

          if (json.trackClusters && typeof json.trackClusters === 'object') setClustersData(json.trackClusters);
          else setClustersData({});

          // trendingKeywordGroups is optional; frontend currently doesn't store it here
      } catch (err) {
        console.error('[HomePage] Failed to load creators', err);
      }
    })();
    return () => { mounted = false };
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <main className="bg-[url('https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=1400&q=80')] bg-cover bg-fixed bg-center bg-no-repeat">
      <div className="backdrop-blur-sm">
        <section className="container mx-auto px-6 pb-16 pt-12">
          <div className="rounded-3xl bg-white/85 p-10 shadow-lg">
            <h1 className="text-4xl font-semibold text-black md:text-5xl">
              {t("hero.title")}
            </h1>
            <p className="mt-4 max-w-3xl text-lg text-black/70">
              {t("hero.subtitle")}
            </p>
            
            {/* 新功能入口 */}
            <div className="mt-6 flex gap-4">
              <Link
                href="/zh/style-generator"
                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-white font-medium hover:bg-blue-700 transition-colors"
              >
                ✨ AI风格生成器
              </Link>
            </div>
          </div>
        </section>

        <section className="container mx-auto px-6 pb-16">
          <div className="rounded-3xl bg-white/90 p-10 shadow-lg">
            <header className="mb-8">
              <h2 className="text-2xl font-semibold text-black">{t("network.title")}</h2>
              <p className="mt-2 max-w-2xl text-sm text-black/60">{t("network.description")}</p>
            </header>
            <CreatorUniverse
              creators={creatorsData}
              edges={edgesData}
              clusters={clustersData}
              trendingKeywords={[]}
            />
          </div>
        </section>
      </div>
      
      {/* 返回顶部按钮 */}
      {showScrollTop && (
        <button
          onClick={scrollToTop}
          className="fixed bottom-8 right-8 z-50 flex h-12 w-12 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg transition-all hover:bg-blue-700 hover:scale-110 active:scale-95"
          aria-label="返回顶部"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2.5}
            stroke="currentColor"
            className="h-6 w-6"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M4.5 15.75l7.5-7.5 7.5 7.5"
            />
          </svg>
        </button>
      )}
    </main>
  );
}
