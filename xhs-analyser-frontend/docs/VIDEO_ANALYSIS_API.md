# 视频分析数据接口文档

## 概述
`GrowthPath` 组件支持传入真实的视频分析数据。本文档说明如何准备和传递数据。

## 数据结构

### 1. VideoAnalysisData (主要接口)

```typescript
interface VideoAnalysisData {
  shots: VideoShot[];                    // 镜头数组
  structureSegments: VideoStructureSegment[];  // 视频结构段落
  totalDuration: string;                 // 总时长 "4:30"
  timeLabels: string[];                  // 时间轴标签
}
```

### 2. VideoShot (镜头数据)

```typescript
interface VideoShot {
  id: number;           // 镜头ID，从1开始
  title: string;        // 镜头标题，如"引入问题"
  subtitle: string;     // 副标题，如"(引入人物的开场)"
  image: string;        // 关键帧图片URL或base64
  narration: string;    // 旁白文案
  timeRange: string;    // 时间范围 "0:00-0:30"
  segmentId: number;    // 所属段落 1-4
}
```

**segmentId 说明:**
- `1` = 开头引言 (蓝色)
- `2` = 核心讲解 (绿色)
- `3` = 案例分析 (紫色)
- `4` = 结尾总结 (橙色)

### 3. VideoStructureSegment (结构段落)

```typescript
interface VideoStructureSegment {
  id: number;                          // 段落ID 1-4
  label: string;                       // 段落名称
  timeRange: string;                   // 时间范围 "(0:00-0:30)"
  color: "blue" | "green" | "purple" | "orange";
  width: string;                       // 宽度百分比 "12.5%"
}
```

## 使用方法

### 方法1: 从API获取数据

```typescript
import { fetchVideoAnalysis } from '@/lib/videoAnalysisAPI';

// 获取视频分析数据
const videoData = await fetchVideoAnalysis('大圆镜科普', 'video_123');

// 传递给组件
<GrowthPath
  followingCreators={creators}
  onSelectCreator={handleSelect}
  videoAnalysis={videoData}
/>
```

### 方法2: 手动构建数据

```typescript
const videoAnalysis: VideoAnalysisData = {
  shots: [
    {
      id: 1,
      title: "开场问候",
      subtitle: "(建立连接)",
      image: "https://your-cdn.com/keyframe1.jpg",
      narration: "大家好，我是XXX...",
      timeRange: "0:00-0:15",
      segmentId: 1
    },
    // ... 更多镜头
  ],
  structureSegments: [
    {
      id: 1,
      label: "开头引言",
      timeRange: "(0:00-0:35)",
      color: "blue",
      width: "14.6%"
    },
    // ... 更多段落
  ],
  totalDuration: "4:00",
  timeLabels: ["0:00", "1:00", "2:00", "3:00", "4:00"]
};
```

### 方法3: 上传关键帧图片

```typescript
import { uploadKeyframesAndCreateAnalysis } from '@/lib/videoAnalysisAPI';

const videoData = await uploadKeyframesAndCreateAnalysis({
  creatorName: "大圆镜科普",
  videoId: "video_123",
  shots: [
    {
      title: "开场问候",
      subtitle: "(建立连接)",
      keyframeFile: imageFile,  // File对象
      narration: "大家好...",
      startTime: "0:00",
      endTime: "0:15",
      segmentId: 1
    },
    // ... 更多镜头
  ]
});
```

## 后端API规范

### 端点: GET /api/video-analysis

**请求参数:**
```
?creator=大圆镜科普&video_id=video_123
```

**返回格式:**
```json
{
  "video_id": "video_123",
  "creator_name": "大圆镜科普",
  "total_duration": "4:00",
  "shots": [
    {
      "shot_id": 1,
      "title": "开场问候",
      "subtitle": "(建立连接)",
      "keyframe_url": "https://cdn.example.com/keyframe1.jpg",
      "narration_text": "大家好，我是XXX...",
      "start_time": "0:00",
      "end_time": "0:15",
      "segment_id": 1
    }
  ],
  "structure": [
    {
      "segment_id": 1,
      "segment_name": "开头引言",
      "start_time": "0:00",
      "end_time": "0:35",
      "color": "blue"
    }
  ]
}
```

### 端点: POST /api/video-analysis/upload

**Content-Type:** `multipart/form-data`

**请求体:**
```
creator_name: "大圆镜科普"
video_id: "video_123"
shots[0][title]: "开场问候"
shots[0][subtitle]: "(建立连接)"
shots[0][keyframe]: <File>
shots[0][narration]: "大家好..."
shots[0][start_time]: "0:00"
shots[0][end_time]: "0:15"
shots[0][segment_id]: 1
...
```

## 图片处理建议

### 1. 使用URL
```typescript
image: "https://your-cdn.com/keyframes/shot1.jpg"
```

### 2. 使用Base64 (小图片)
```typescript
image: "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
```

### 3. 图片尺寸建议
- 宽度: 400-800px
- 高宽比: 16:9
- 格式: JPG/PNG/WebP
- 大小: < 200KB

## 完整示例

```typescript
const exampleData: VideoAnalysisData = {
  shots: [
    {
      id: 1,
      title: "开场问候",
      subtitle: "(建立连接)",
      image: "https://cdn.example.com/shot1.jpg",
      narration: "大家好，我是XXX，今天给大家分享...",
      timeRange: "0:00-0:15",
      segmentId: 1
    },
    {
      id: 2,
      title: "提出问题",
      subtitle: "(引发思考)",
      image: "https://cdn.example.com/shot2.jpg",
      narration: "你有没有想过，为什么...",
      timeRange: "0:15-0:35",
      segmentId: 1
    },
    {
      id: 3,
      title: "原理讲解",
      subtitle: "(科学知识)",
      image: "https://cdn.example.com/shot3.jpg",
      narration: "这个现象背后的原理是...",
      timeRange: "0:35-1:30",
      segmentId: 2
    }
  ],
  structureSegments: [
    {
      id: 1,
      label: "开头引言",
      timeRange: "(0:00-0:35)",
      color: "blue",
      width: "14.6%"
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
```

## 注意事项

1. **镜头ID必须连续**: 从1开始，不能跳号
2. **segmentId范围**: 必须是1-4之间
3. **时间格式**: 统一使用 "mm:ss" 或 "h:mm:ss"
4. **宽度总和**: structureSegments的width总和应接近100%
5. **图片URL**: 确保可访问且支持CORS
6. **Base64限制**: 仅用于小图片（<100KB）

## 辅助工具

项目提供了 `transformAPIResponse` 函数来转换后端API返回的数据:

```typescript
import { transformAPIResponse } from '@/types/videoAnalysis';

const apiData = await fetch('/api/video-analysis').then(r => r.json());
const componentData = transformAPIResponse(apiData);
```
