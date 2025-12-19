/**
 * 视频分析数据类型定义
 * 用于传递真实的视频分析数据到GrowthPath组件
 */

export interface VideoShot {
  id: number;                 // 镜头ID，从1开始
  title: string;              // 镜头标题，如"引入问题"
  subtitle: string;           // 镜头副标题，如"(引入人物的开场)"
  image: string;              // 关键帧图片URL或base64编码的图片
  narration: string;          // 该镜头的旁白文案
  timeRange: string;          // 时间范围，如"0:00-0:30"
  segmentId: number;          // 所属的视频结构段落ID (1=开头引言, 2=核心讲解, 3=案例分析, 4=结尾总结)
}

export interface VideoStructureSegment {
  id: number;                 // 段落ID (1-4)
  label: string;              // 段落标签，如"开头引言"、"核心讲解"、"案例分析"、"结尾总结"
  timeRange: string;          // 时间范围，如"(0:00-0:30)"
  color: "blue" | "green" | "purple" | "orange";  // 显示颜色
  width: string;              // 在时间轴上的宽度百分比，如"12.5%"
}

export interface VideoAnalysisData {
  shots: VideoShot[];                           // 所有镜头数据
  structureSegments: VideoStructureSegment[];   // 视频结构段落
  totalDuration: string;                        // 视频总时长，如"4:30"
  timeLabels: string[];                         // 时间轴标签，如["0:00", "1:00", "2:00", "3:00", "4:00", "4:30"]
  // 可选的笔记信息（由后端注入）
  note?: {
    note_id?: string;
    title?: string;
    desc?: string;
    video_url?: string;
    note_url?: string;
    cover?: string;
    liked_count?: number;
    collected_count?: number;
    comment_count?: number;
    share_count?: number;
    user_id?: string;
    create_time?: string;
  };
}

/**
 * API返回的原始数据格式示例
 * 你的后端API应该返回这种格式的数据
 */
export interface VideoAnalysisAPIResponse {
  video_id: string;
  creator_name: string;
  total_duration: string;
  shots: Array<{
    shot_id: number;
    title: string;
    subtitle: string;
    keyframe_url: string;      // 关键帧图片的URL
    narration_text: string;    // 旁白文案
    start_time: string;        // 开始时间，如"0:00"
    end_time: string;          // 结束时间，如"0:30"
    segment_id: number;        // 所属段落ID
  }>;
  structure: Array<{
    segment_id: number;
    segment_name: string;
    start_time: string;
    end_time: string;
    color: "blue" | "green" | "purple" | "orange";
  }>;
}

/**
 * 将API返回的数据转换为组件需要的格式
 */
export function transformAPIResponse(apiData: VideoAnalysisAPIResponse): VideoAnalysisData {
  // 转换镜头数据
  const shots: VideoShot[] = apiData.shots.map(shot => ({
    id: shot.shot_id,
    title: shot.title,
    subtitle: shot.subtitle,
    image: shot.keyframe_url,
    narration: shot.narration_text,
    timeRange: `${shot.start_time}-${shot.end_time}`,
    segmentId: shot.segment_id
  }));

  // 计算每个段落的宽度百分比
  const totalSeconds = parseDuration(apiData.total_duration);
  const structureSegments: VideoStructureSegment[] = apiData.structure.map(seg => {
    const startSeconds = parseDuration(seg.start_time);
    const endSeconds = parseDuration(seg.end_time);
    const duration = endSeconds - startSeconds;
    const widthPercent = (duration / totalSeconds * 100).toFixed(1);

    return {
      id: seg.segment_id,
      label: seg.segment_name,
      timeRange: `(${seg.start_time}-${seg.end_time})`,
      color: seg.color,
      width: `${widthPercent}%`
    };
  });

  // 生成时间轴标签
  const timeLabels = generateTimeLabels(totalSeconds);

  return {
    shots,
    structureSegments,
    totalDuration: apiData.total_duration,
    timeLabels
  };
}

/**
 * 辅助函数：将时间字符串转换为秒数
 */
function parseDuration(timeStr: string): number {
  const parts = timeStr.split(':').map(Number);
  if (parts.length === 2) {
    return parts[0] * 60 + parts[1]; // mm:ss
  } else if (parts.length === 3) {
    return parts[0] * 3600 + parts[1] * 60 + parts[2]; // hh:mm:ss
  }
  return 0;
}

/**
 * 辅助函数：生成均匀分布的时间标签
 */
function generateTimeLabels(totalSeconds: number): string[] {
  const labels: string[] = [];
  const intervals = 5; // 生成6个标签（包括起点和终点）
  
  for (let i = 0; i <= intervals; i++) {
    const seconds = Math.floor((totalSeconds / intervals) * i);
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    labels.push(`${mins}:${secs.toString().padStart(2, '0')}`);
  }
  
  return labels;
}
