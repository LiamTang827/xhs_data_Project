import Link from "next/link";
import { notFound } from "next/navigation";
import type { CreatorNode } from "@/data/creators";
import { MongoClient } from 'mongodb';

const MONGO_URI = process.env.MONGO_URI;
const DB_NAME = process.env.MONGO_DB || 'media_crawler';
const CREATOR_COLLECTION = process.env.CREATOR_COLLECTION || 'xhs_users';

async function fetchAllCreators(): Promise<CreatorNode[]> {
  if (!MONGO_URI) return [];
  const client = new MongoClient(MONGO_URI);
  await client.connect();
  const db = client.db(DB_NAME);
  const docs = await db.collection(CREATOR_COLLECTION).find({}).toArray();
  await client.close();
  return docs.map((doc: any) => ({
    id: doc.user_id || doc._id?.toString(),
    name: doc.nickname || '',
    followers: Number(doc.fans || doc.followers || 0),
    totalEngagement: Number(doc.totalEngagement || doc.interaction || doc.engagement || 0),
    engagementIndex: Number(doc.interaction || doc.engagement || 0),  // 兼容旧数据
    primaryTrack: doc.primaryTrack || '其他',
    contentForm: doc.contentForm || '创作者',
    recentKeywords: Array.isArray(doc.tag_list) ? doc.tag_list : (doc.tag_list ? JSON.parse(doc.tag_list || '[]') : []),
    position: { x: 0, y: 0 },
    avatar: doc.avatar || '',
    ipLocation: doc.ip_location || '',
    desc: doc.desc || '',
    redId: doc.redId || '',
  }));
}

interface PageProps {
  params: Promise<{ locale: string; id: string }>;
}

export default async function CreatorDetailPage({ params }: PageProps) {
  const { locale, id } = await params;
  const creators = await fetchAllCreators();
  const creator = creators.find((c) => c.id === id);

  if (!creator) notFound();

  // For related creators we generate simple edges on the fly (or you can store edges in DB)
  const relatedCreators = creators.filter((c) => c.primaryTrack === creator.primaryTrack && c.id !== creator.id).slice(0, 8);

  return (
    <main className="container mx-auto px-6 py-12">
      <Link href={`/${locale}`} className="text-sm text-blue-600 hover:text-blue-700">
        ← 返回星图
      </Link>

      <section className="mt-6 grid gap-10 rounded-3xl bg-white p-10 shadow-lg lg:grid-cols-[2fr_1fr]">
        <div>
          <h1 className="text-3xl font-semibold text-black">{creator.name}</h1>
          <div className="mt-3 flex flex-wrap gap-4 text-sm text-black/60">
            <span>粉丝数：{creator.followers.toLocaleString()}</span>
            <span>总互动数：{(creator.totalEngagement || creator.engagementIndex || 0).toLocaleString()}</span>
            <span>内容形式：{creator.contentForm}</span>
          </div>

          <div className="mt-6">
            <h2 className="text-lg font-semibold text-black">近期关键词</h2>
            <div className="mt-3 flex flex-wrap gap-2">
              {creator.recentKeywords.map((keyword) => (
                <span key={`${creator.id}-${keyword}`} className="rounded-full bg-black/10 px-3 py-1 text-xs text-black/70">#{keyword}</span>
              ))}
            </div>
          </div>

          <div className="mt-8">
            <h2 className="text-lg font-semibold text-black">内容风格与形式</h2>
            <p className="mt-3 rounded-2xl bg-black/5 p-4 text-sm text-black/70">
              该创作者以「{creator.primaryTrack}」赛道为主，核心内容形态为「{creator.contentForm}」。结合近期关键词来看，粉丝对「{creator.recentKeywords.slice(0, 2).join("、")}"的兴趣持续升温，可重点关注合作机会。
            </p>
          </div>
        </div>

        <aside className="space-y-4">
          <div className="rounded-2xl border border-black/10 bg-black/5 p-5">
            <h3 className="text-sm font-semibold text-black/70">算法关联创作者</h3>
            <ul className="mt-4 space-y-2 text-sm">
              {relatedCreators.map((item) => (
                <li key={item.id} className="flex justify-between text-black/70">
                  <Link href={`/${locale}/creators/${item.id}`} className="text-blue-600 hover:text-blue-700">{item.name}</Link>
                  <span className="text-xs text-black/40">相关度 0.00</span>
                </li>
              ))}
            </ul>
          </div>
        </aside>
      </section>
    </main>
  );
}
