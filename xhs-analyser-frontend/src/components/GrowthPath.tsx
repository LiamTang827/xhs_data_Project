import type { CreatorNode } from "@/data/creators";

interface GrowthPathProps {
  userProfile?: {
    estimatedFollowers: number;
    interestedTracks: string[];
  };
  followingCreators: CreatorNode[];
  onSelectCreator: (id: string) => void;
}

export function GrowthPath({ userProfile, followingCreators, onSelectCreator }: GrowthPathProps) {
  // Find "大圆镜科普" or fallback to the first one
  const targetCreator = followingCreators.find(c => c.name === "大圆镜科普") || followingCreators[0];

  return (
    <section className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm">
      <header className="mb-6">
        <h2 className="text-2xl font-semibold text-black">🎯 你的成长路径推荐</h2>
      </header>

      <div className="rounded-xl border-2 border-green-300 bg-gradient-to-br from-green-50 to-emerald-50 shadow-md p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-black">
            【学习期】打好基础
          </h3>
          <span className="rounded-full bg-green-500 px-3 py-1 text-sm font-medium text-white">
            当前
          </span>
        </div>

        {/* 学习对象 */}
        <div className="mt-4">
          <h4 className="text-sm font-semibold text-black">🎓 学习对象</h4>
          <div className="mt-2">
            {targetCreator ? (
              <button
                type="button"
                onClick={() => onSelectCreator(targetCreator.id)}
                className="flex w-full items-center gap-3 rounded-lg border border-black/10 bg-white p-3 text-left transition-all hover:border-blue-300 hover:shadow-md"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-600">
                  {targetCreator.name.charAt(0)}
                </div>
                <div className="flex-1">
                  <div className="font-semibold text-black">{targetCreator.name}</div>
                  <div className="text-xs text-black/50">
                    {targetCreator.followers >= 10000 
                      ? `${Math.round(targetCreator.followers / 10000)}万粉` 
                      : `${targetCreator.followers}粉`}
                  </div>
                </div>
                <div className="text-sm text-blue-600">查看 →</div>
              </button>
            ) : (
              <div className="text-sm text-gray-500">未找到推荐的学习对象</div>
            )}
          </div>
        </div>

        {/* 学习建议 */}
        <div className="mt-6">
          <h4 className="text-sm font-semibold text-black mb-2">💡 学习建议</h4>
          <ul className="space-y-2 text-sm text-black/70">
            <li>• 分析优秀创作者的内容结构和呈现方式</li>
            <li>• 学习如何与目标受众建立连接</li>
            <li>• 持续输出高质量内容</li>
          </ul>
        </div>
      </div>
    </section>
  );
}
