/**
 * 视频分析API使用示例
 * 展示如何从后端获取数据并传递给GrowthPath组件
 */

import { VideoAnalysisData, VideoAnalysisAPIResponse, transformAPIResponse } from '@/types/videoAnalysis';

/**
 * 示例1: 从API获取视频分析数据
 */
export async function fetchVideoAnalysis(creatorName: string, videoId: string): Promise<VideoAnalysisData> {
  try {
    // 调用你的后端API
    const response = await fetch(`/api/video-analysis?creator=${encodeURIComponent(creatorName)}&video_id=${videoId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch video analysis');
    }
    
    const apiData: VideoAnalysisAPIResponse = await response.json();
    
    // 转换为组件需要的格式
    return transformAPIResponse(apiData);
  } catch (error) {
    console.error('Error fetching video analysis:', error);
    throw error;
  }
}

/**
 * 示例2: 手动构建视频分析数据（用于测试）
 */
export function createManualVideoAnalysis(): VideoAnalysisData {
  return {
    shots: [
      {
        id: 1,
        title: "开场问候",
        subtitle: "(建立连接)",
        image: "/path/to/keyframe1.jpg",  // 或者 "data:image/jpeg;base64,..."
        narration: "大家好，我是XXX，今天给大家分享一个非常有趣的科学现象...",
        timeRange: "0:00-0:15",
        segmentId: 1
      },
      {
        id: 2,
        title: "提出问题",
        subtitle: "(引发思考)",
        image: "/path/to/keyframe2.jpg",
        narration: "你有没有想过，为什么天空是蓝色的？这背后其实有着深刻的物理原理...",
        timeRange: "0:15-0:35",
        segmentId: 1
      },
      {
        id: 3,
        title: "原理讲解",
        subtitle: "(科学知识)",
        image: "/path/to/keyframe3.jpg",
        narration: "这个现象叫做瑞利散射。当太阳光进入大气层时...",
        timeRange: "0:35-1:30",
        segmentId: 2
      },
      // ... 更多镜头
    ],
    structureSegments: [
      {
        id: 1,
        label: "开头引言",
        timeRange: "(0:00-0:35)",
        color: "blue",
        width: "14.6%"  // (35秒 / 240秒总时长) * 100
      },
      {
        id: 2,
        label: "核心讲解",
        timeRange: "(0:35-2:30)",
        color: "green",
        width: "47.9%"
      },
      {
        id: 3,
        label: "案例分析",
        timeRange: "(2:30-3:40)",
        color: "purple",
        width: "29.2%"
      },
      {
        id: 4,
        label: "结尾总结",
        timeRange: "(3:40-4:00)",
        color: "orange",
        width: "8.3%"
      }
    ],
    totalDuration: "4:00",
    timeLabels: ["0:00", "0:48", "1:36", "2:24", "3:12", "4:00"]
  };
}

/**
 * 示例3: 上传关键帧图片并创建视频分析
 */
export async function uploadKeyframesAndCreateAnalysis(data: {
  creatorName: string;
  videoId: string;
  shots: Array<{
    title: string;
    subtitle: string;
    keyframeFile: File;        // 图片文件
    narration: string;
    startTime: string;
    endTime: string;
    segmentId: number;
  }>;
}): Promise<VideoAnalysisData> {
  const formData = new FormData();
  
  formData.append('creator_name', data.creatorName);
  formData.append('video_id', data.videoId);
  
  // 添加每个镜头的数据和图片
  data.shots.forEach((shot, index) => {
    formData.append(`shots[${index}][title]`, shot.title);
    formData.append(`shots[${index}][subtitle]`, shot.subtitle);
    formData.append(`shots[${index}][keyframe]`, shot.keyframeFile);
    formData.append(`shots[${index}][narration]`, shot.narration);
    formData.append(`shots[${index}][start_time]`, shot.startTime);
    formData.append(`shots[${index}][end_time]`, shot.endTime);
    formData.append(`shots[${index}][segment_id]`, shot.segmentId.toString());
  });
  
  const response = await fetch('/api/video-analysis/upload', {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    throw new Error('Failed to upload video analysis');
  }
  
  const apiData: VideoAnalysisAPIResponse = await response.json();
  return transformAPIResponse(apiData);
}

/**
 * 示例4: 在React组件中使用
 * 
 * ```tsx
 * import { GrowthPath } from '@/components/GrowthPath';
 * import { fetchVideoAnalysis } from '@/lib/videoAnalysisAPI';
 * import { useState, useEffect } from 'react';
 * 
 * function MyComponent() {
 *   const [videoData, setVideoData] = useState(null);
 * 
 *   useEffect(() => {
 *     fetchVideoAnalysis('大圆镜科普', 'video_123')
 *       .then(data => setVideoData(data))
 *       .catch(err => console.error(err));
 *   }, []);
 * 
 *   return (
 *     <GrowthPath
 *       followingCreators={creators}
 *       onSelectCreator={handleSelect}
 *       videoAnalysis={videoData}  // 传入视频分析数据
 *     />
 *   );
 * }
 * ```
 */
