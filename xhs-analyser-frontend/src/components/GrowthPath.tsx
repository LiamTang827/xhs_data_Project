import { useState } from "react";
import type { CreatorNode } from "@/data/creators";

// 视频分析数据接口定义
export interface VideoShot {
  id: number;
  title: string;              // 镜头标题，如"引入问题"
  subtitle: string;           // 镜头副标题，如"(引入人物的开场)"
  image: string;              // 关键帧图片URL或base64
  narration: string;          // 该镜头的旁白文案
  timeRange: string;          // 时间范围，如"0:00-0:30"
  segmentId: number;          // 所属的视频结构段落ID (1-4)
}

export interface VideoStructureSegment {
  id: number;
  label: string;              // 段落标签，如"开头引言"
  timeRange: string;          // 时间范围，如"(0:00-0:30)"
  color: "blue" | "green" | "purple" | "orange";  // 显示颜色
  width: string;              // 在时间轴上的宽度百分比
}

export interface VideoAnalysisData {
  shots: VideoShot[];                           // 所有镜头数据
  structureSegments: VideoStructureSegment[];   // 视频结构段落
  totalDuration: string;                        // 视频总时长，如"4:30"
  timeLabels: string[];                         // 时间轴标签，如["0:00", "1:00", ...]
}

interface GrowthPathProps {
  userProfile?: {
    estimatedFollowers: number;
    interestedTracks: string[];
  };
  followingCreators: CreatorNode[];
  onSelectCreator: (id: string) => void;
  videoAnalysis?: VideoAnalysisData;  // 可选的视频分析数据
}

interface Shot {
  id: number;
  title: string;
  subtitle: string;
  image: string;
  narration: string;
  timeRange: string;
}

const shots: Shot[] = [
  {
    id: 1,
    title: "引入问题",
    subtitle: "(引入人物的开场)",
    image: "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=400&h=225&fit=crop",
    narration: "大家好，今天我们来聊聊一个有趣的现象。你有没有想过为什么...",
    timeRange: "0:00-0:20"
  },
  {
    id: 2,
    title: "问题展开",
    subtitle: "(设置悬念)",
    image: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&h=225&fit=crop",
    narration: "这个问题困扰了很多人，今天我们就来揭开这个谜底...",
    timeRange: "0:20-0:40"
  },
  {
    id: 3,
    title: "展示现象",
    subtitle: "(科学原理)",
    image: "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=400&h=225&fit=crop",
    narration: "这个现象背后的原理其实非常简单。从物理学角度来看...",
    timeRange: "0:40-1:10"
  },
  {
    id: 4,
    title: "专家解读",
    subtitle: "(深入讲述)",
    image: "https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=400&h=225&fit=crop",
    narration: "让我们深入了解一下。根据最新的研究表明，这涉及到...",
    timeRange: "1:10-1:45"
  },
  {
    id: 5,
    title: "数据佐证",
    subtitle: "(权威支持)",
    image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=225&fit=crop",
    narration: "根据统计数据显示，这个理论得到了充分的验证...",
    timeRange: "1:45-2:15"
  },
  {
    id: 6,
    title: "动画演示",
    subtitle: "(形象直观)",
    image: "https://images.unsplash.com/photo-1550985616-10810253b84d?w=400&h=225&fit=crop",
    narration: "通过这个动画，我们可以更直观地看到整个过程是如何发生的...",
    timeRange: "2:15-2:50"
  },
  {
    id: 7,
    title: "实验演示",
    subtitle: "(实际操作)",
    image: "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=400&h=225&fit=crop",
    narration: "现在让我们通过一个简单的实验来验证这个理论...",
    timeRange: "2:50-3:20"
  },
  {
    id: 8,
    title: "案例分析",
    subtitle: "(实际应用)",
    image: "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=400&h=225&fit=crop",
    narration: "在实际生活中，我们可以看到这个原理的应用。比如说...",
    timeRange: "3:20-3:50"
  },
  {
    id: 9,
    title: "总结回顾",
    subtitle: "(知识梳理)",
    image: "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400&h=225&fit=crop",
    narration: "让我们回顾一下今天学到的重点内容...",
    timeRange: "3:50-4:15"
  },
  {
    id: 10,
    title: "结尾总结",
    subtitle: "(点题升华)",
    image: "https://images.unsplash.com/photo-1516339901601-2e1b62dc0c45?w=400&h=225&fit=crop",
    narration: "总结一下，今天我们学到了...希望这个视频对你有帮助，记得点赞关注！",
    timeRange: "4:15-4:30"
  }
];

// Map shots to structure segments
const shotToSegmentMap: Record<number, number> = {
  1: 1,  // 镜头1 -> 开头引言
  2: 1,  // 镜头2 -> 开头引言
  3: 2,  // 镜头3 -> 核心讲解
  4: 2,  // 镜头4 -> 核心讲解
  5: 2,  // 镜头5 -> 核心讲解
  6: 3,  // 镜头6 -> 案例分析
  7: 3,  // 镜头7 -> 案例分析
  8: 3,  // 镜头8 -> 案例分析
  9: 4,  // 镜头9 -> 结尾总结
  10: 4  // 镜头10 -> 结尾总结
};

const structureSegments = [
  { id: 1, label: "开头引言", timeRange: "(0:00-0:30)", color: "blue" as const, width: "12.5%" },
  { id: 2, label: "核心讲解", timeRange: "(0:30-2:00)", color: "green" as const, width: "37.5%" },
  { id: 3, label: "案例分析", timeRange: "(2:00-3:30)", color: "purple" as const, width: "32.5%" },
  { id: 4, label: "结尾总结", timeRange: "(3:30-4:00)", color: "orange" as const, width: "17.5%" }
];

export function GrowthPath({ userProfile, followingCreators, onSelectCreator, videoAnalysis }: GrowthPathProps) {
  const [selectedShot, setSelectedShot] = useState<number | null>(null);
  
  // API基础URL
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';
  
  // 使用传入的数据或默认数据
  const shotsData = videoAnalysis?.shots || shots;
  const segmentsData = videoAnalysis?.structureSegments || structureSegments;
  const timeLabelsData = videoAnalysis?.timeLabels || ["0:00", "1:00", "2:00", "3:00", "4:00", "4:30"];
  
  // 构建镜头到段落的映射
  const shotToSegmentMap: Record<number, number> = {};
  if (videoAnalysis?.shots) {
    videoAnalysis.shots.forEach(shot => {
      shotToSegmentMap[shot.id] = shot.segmentId;
    });
  } else {
    // 默认映射
    [1, 2].forEach(id => shotToSegmentMap[id] = 1);
    [3, 4, 5].forEach(id => shotToSegmentMap[id] = 2);
    [6, 7, 8].forEach(id => shotToSegmentMap[id] = 3);
    [9, 10].forEach(id => shotToSegmentMap[id] = 4);
  }
  
  // Automatically determine active segment based on selected shot
  const activeSegment = selectedShot ? shotToSegmentMap[selectedShot] : null;
  
  // Find "大圆镜科普" or fallback to the first one if not found (though user requested specific one)
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

          {/* 作品分析 */}
          <div className="mt-6">
            <h4 className="text-sm font-semibold text-black mb-3">📊 作品分析</h4>
            
            {/* Analysis Container */}
            <div className="rounded-lg bg-black p-6 text-sm">
              {/* Title Section */}
              <div className="mb-4">
                <h5 className="text-white font-semibold text-base mb-2">镜头分解</h5>
              </div>

              {/* Note info (if provided by backend) */}
              {videoAnalysis?.note && (
                <div className="mb-4 flex items-center gap-4 border-b border-gray-800 pb-4">
                  {/* 视频图标替代封面（小红书CDN有防盗链） */}
                  <div className="w-20 h-14 bg-gradient-to-br from-red-500 to-pink-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <span className="text-2xl">🎬</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold text-white truncate">{videoAnalysis.note.title || '作品分析'}</div>
                    <div className="text-xs text-gray-400 line-clamp-1 mt-1">{videoAnalysis.note.desc}</div>
                    <div className="mt-2 text-xs text-gray-400 flex gap-3">
                      <span>👍 {videoAnalysis.note.liked_count ?? 0}</span>
                      <span>⭐ {videoAnalysis.note.collected_count ?? 0}</span>
                      <span>💬 {videoAnalysis.note.comment_count ?? 0}</span>
                      <span>🔄 {(videoAnalysis.note as { share_count?: number })?.share_count ?? 0}</span>
                    </div>
                  </div>
                  {(videoAnalysis.note as { note_url?: string })?.note_url && (
                    <a href={(videoAnalysis.note as { note_url?: string }).note_url} target="_blank" rel="noreferrer" className="text-sm text-blue-400 whitespace-nowrap hover:text-blue-300 transition-colors">打开作品 →</a>
                  )}
                </div>
              )}

              {/* Shots Grid - Horizontal Scroll */}
              <div className="relative mb-6">
                <div className="overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800">
                  <div className="flex gap-3 min-w-max px-1">
                    {shotsData.map((shot) => (
                      <button
                        key={shot.id}
                        type="button"
                        onClick={() => setSelectedShot(shot.id)}
                        className={`flex flex-col items-center transition-all cursor-pointer flex-shrink-0 w-[160px] ${
                          selectedShot === shot.id ? 'scale-105' : 'hover:scale-102'
                        }`}
                      >
                        <div className={`relative w-full aspect-video rounded-lg overflow-hidden mb-2 border-2 transition-all ${
                          selectedShot === shot.id ? 'border-blue-400 shadow-lg shadow-blue-500/50' : 'border-transparent'
                        }`}>
                          <img 
                            src={shot.image.startsWith('http') ? shot.image : `${API_BASE_URL}${shot.image}`} 
                            alt={shot.title}
                            className="w-full h-full object-cover"
                          />
                          {selectedShot === shot.id && (
                            <div className="absolute inset-0 bg-blue-500/20 flex items-center justify-center">
                              <div className="bg-blue-500 text-white px-2 py-1 rounded text-xs font-semibold">
                                ▶ 播放中
                              </div>
                            </div>
                          )}
                        </div>
                        <p className={`text-xs text-center leading-tight transition-colors ${
                          selectedShot === shot.id ? 'text-blue-300' : 'text-white'
                        }`}>
                          <span className="font-semibold">镜头{shot.id}:</span> {shot.title}<br/>
                          <span className="text-gray-400">{shot.subtitle}</span>
                        </p>
                      </button>
                    ))}
                  </div>
                </div>
                {/* Scroll Hint */}
                <div className="absolute right-0 top-0 bottom-2 w-12 bg-gradient-to-l from-black to-transparent pointer-events-none flex items-center justify-end pr-2">
                  <span className="text-gray-400 text-xl">›</span>
                </div>
              </div>

              {/* Video Structure Timeline */}
              <div>
                <h5 className="text-white font-semibold text-base mb-3">视频结构</h5>
                
                {/* Timeline Bar */}
                <div className="relative h-12 rounded-lg overflow-hidden border border-gray-700">
                  {/* Segments */}
                  <div className="absolute inset-0 flex">
                    {segmentsData.map((segment) => {
                      const isActive = activeSegment === segment.id;
                      const colorMap = {
                        blue: 'from-blue-500 to-blue-600',
                        green: 'from-green-500 to-green-600',
                        purple: 'from-purple-500 to-purple-600',
                        orange: 'from-orange-500 to-orange-600'
                      };
                      
                      return (
                        <div
                          key={segment.id}
                          className={`flex items-center justify-center transition-all ${
                            isActive 
                              ? `bg-gradient-to-r ${colorMap[segment.color as keyof typeof colorMap]}` 
                              : 'bg-gray-700'
                          }`}
                          style={{ width: segment.width }}
                        >
                          <span className={`text-xs font-medium transition-colors ${
                            isActive ? 'text-white' : 'text-gray-400'
                          }`}>
                            {segment.label}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Time Labels */}
                <div className="relative mt-2 flex justify-between text-xs text-gray-400">
                  {timeLabelsData.map((label, idx) => (
                    <span key={idx}>{label}</span>
                  ))}
                </div>

                {/* Time Markers with Descriptions */}
                <div className="mt-4 grid grid-cols-4 gap-2 text-xs">
                  {segmentsData.map((segment) => {
                    const colorMap = {
                      blue: 'text-blue-400',
                      green: 'text-green-400',
                      purple: 'text-purple-400',
                      orange: 'text-orange-400'
                    };
                    
                    return (
                      <div key={segment.id} className="text-gray-300">
                        <span className={`font-semibold ${activeSegment === segment.id ? colorMap[segment.color as keyof typeof colorMap] : 'text-gray-500'}`}>
                          {segment.label}
                        </span>
                        <span className="text-gray-400"> {segment.timeRange}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Narration Display */}
              {selectedShot && (
                <div className="mt-6 p-4 bg-gray-900 rounded-lg border border-gray-700 animate-fadeIn">
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
                        <span className="text-white text-sm font-bold">{selectedShot}</span>
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h6 className="text-blue-400 font-semibold text-sm">
                          镜头{selectedShot}: {shotsData.find(s => s.id === selectedShot)?.title}
                        </h6>
                        <span className="text-gray-500 text-xs">
                          {shotsData.find(s => s.id === selectedShot)?.timeRange}
                        </span>
                      </div>
                      <p className="text-gray-300 text-sm leading-relaxed">
                        📝 <span className="font-semibold text-gray-400">旁白文案:</span> {shotsData.find(s => s.id === selectedShot)?.narration}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
      </div>
    </section>
  );
}
