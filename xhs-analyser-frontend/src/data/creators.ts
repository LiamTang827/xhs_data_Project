// 此文件由脚本自动生成
// 生成时间: 2026/01/18 00:53:27
// 数据来源: data-analysiter

export interface CreatorNode {
  id: string;
  name: string;
  followers: number;
  fansGrowth7d?: number;  // 7天粉丝增长数
  totalEngagement?: number;  // 最近30天总互动数
  totalLikes?: number;
  totalCollects?: number;
  totalComments?: number;
  totalShares?: number;
  noteCount?: number;  // 最近30天笔记数
  engagementIndex?: number;  // 兼容旧数据
  primaryTrack: string;
  contentForm: string;
  recentKeywords: string[];
  position: { x: number; y: number };
  avatar?: string;
  ipLocation?: string;
  desc?: string;
  redId?: string;
  topics?: string[];
  indexSeries?: Array<{ ts: number; value: number }>;
}

export type CreatorEdgeSignal = "keyword" | "audience" | "style" | "campaign";

export interface CreatorEdge {
  source: string;
  target: string;
  weight: number;
  types: Partial<Record<CreatorEdgeSignal, number>>;
  sampleEvents?: Array<{
    type: CreatorEdgeSignal;
    title: string;
    timestamp: string;
  }>;
}

export const creators: CreatorNode[] = [
  {
    "id": "5ff98b9d0000000001008f40",
    "name": "星球研究所InstituteforPlanet",
    "followers": 1005057,
    "engagementIndex": 3358603,
    "primaryTrack": "中国地理与自然景观",
    "contentForm": "专业科普与知识传播, 视觉震撼与宏大叙事, 数据支撑与事实论证, 情感共鸣与家国情怀, 系列化栏目运营, 多语言国际化表达",
    "recentKeywords": [],
    "position": {
      "x": 80,
      "y": 93
    },
    "avatar": "https://sns-avatar-qc.xhscdn.com/avatar/1040g2jo31c2kka15h0005nvpheeg93q0419vqv8?imageView2/2/w/360/format/webp",
    "desc": "热爱人类，热爱地球。",
    "ipLocation": "北京"
  },
  {
    "id": "57576ed25e87e7791b68777d",
    "name": "硅谷樱花小姐姐🌸",
    "followers": 0,
    "engagementIndex": 0,
    "primaryTrack": "硅谷",
    "contentForm": "未知",
    "recentKeywords": [],
    "position": {
      "x": 74,
      "y": 65
    },
    "avatar": "",
    "desc": "",
    "ipLocation": ""
  },
  {
    "id": "5ef2ec930000000001005fe2",
    "name": "无穷小亮的科普日常",
    "followers": 0,
    "engagementIndex": 0,
    "primaryTrack": "生物鉴定",
    "contentForm": "专业科普, 幽默风趣, 实地拍摄, 系列化内容, 互动性强, 通俗易懂, 视觉化呈现, 话题标签运营",
    "recentKeywords": [],
    "position": {
      "x": 22,
      "y": 40
    },
    "avatar": "",
    "desc": "",
    "ipLocation": ""
  },
  {
    "id": "5b21847911be1079a51a573c",
    "name": "小熊说你超有爱",
    "followers": 0,
    "engagementIndex": 0,
    "primaryTrack": "创业招募",
    "contentForm": "未知",
    "recentKeywords": [],
    "position": {
      "x": 10,
      "y": 60
    },
    "avatar": "",
    "desc": "",
    "ipLocation": ""
  },
  {
    "id": "5abf90244eacab2c32c7c5e6",
    "name": "小Lin说",
    "followers": 1884802,
    "engagementIndex": 4003332,
    "primaryTrack": "商业分析",
    "contentForm": "未知",
    "recentKeywords": [
      "北京大学"
    ],
    "position": {
      "x": 56,
      "y": 88
    },
    "avatar": "https://sns-avatar-qc.xhscdn.com/avatar/616ee14936ede13faad1038e.jpg?imageView2/2/w/360/format/webp",
    "desc": "商业财经不无聊～\n💗北大-＞哥大-＞JPMorgan->创业\n对后期感兴趣的小伙伴可以联系：xiaolin_recruiting@163.com\n‼️无小号，不会以任何方式私信粉丝，谨防受骗~",
    "ipLocation": "北京"
  },
  {
    "id": "66d6aedc000000001e00f94d",
    "name": "大圆镜科普",
    "followers": 27048,
    "engagementIndex": 136119,
    "primaryTrack": "脑科学与神经科学",
    "contentForm": "诗意化科学叙述，富有文学性和哲学深度",
    "recentKeywords": [
      "30岁",
      "上海静安"
    ],
    "position": {
      "x": 35,
      "y": 41
    },
    "avatar": "https://sns-avatar-qc.xhscdn.com/avatar/1040g2jo31k07dtepj46g5pmmlre7huadb3030a8?imageView2/2/w/360/format/webp",
    "desc": "科技之大，艺术之圆，哲学之镜\n天桥脑科学研究院大圆镜工作室“用AI做最好的视频”\n（每周六日双更）",
    "ipLocation": "上海"
  },
  {
    "id": "586f442550c4b43de8f114b0",
    "name": "Ada在美国",
    "followers": 0,
    "engagementIndex": 0,
    "primaryTrack": "美国生活",
    "contentForm": "未知",
    "recentKeywords": [],
    "position": {
      "x": 36,
      "y": 21
    },
    "avatar": "",
    "desc": "",
    "ipLocation": ""
  },
  {
    "id": "5e818a5d0000000001006e10",
    "name": "所长林超",
    "followers": 1118568,
    "engagementIndex": 2448656,
    "primaryTrack": "就业与职业发展",
    "contentForm": "深度分析型, 数据驱动解读, 趋势预测导向, 实用指导性, 政策解读专业, 跨学科视角, 通俗易懂表达, 正能量激励, 社会热点追踪, 解决方案提供",
    "recentKeywords": [
      "摩羯座"
    ],
    "position": {
      "x": 60,
      "y": 85
    },
    "avatar": "https://sns-avatar-qc.xhscdn.com/avatar/63907ba4ead25995c5dd9dfb.jpg?imageView2/2/w/360/format/webp",
    "desc": "《跨学科通识课》及新书《开窍》已上线\n薛定谔的眨眼，看科技&商业原理",
    "ipLocation": ""
  }
];

export const creatorEdges: CreatorEdge[] = [
  {
    "source": "5ff98b9d0000000001008f40",
    "target": "5ef2ec930000000001005fe2",
    "weight": 0.8,
    "types": {
      "style": 1
    }
  },
  {
    "source": "5ff98b9d0000000001008f40",
    "target": "66d6aedc000000001e00f94d",
    "weight": 0.76,
    "types": {
      "style": 1
    }
  },
  {
    "source": "5ff98b9d0000000001008f40",
    "target": "586f442550c4b43de8f114b0",
    "weight": 0.71,
    "types": {
      "style": 1
    }
  },
  {
    "source": "5ef2ec930000000001005fe2",
    "target": "57576ed25e87e7791b68777d",
    "weight": 0.7,
    "types": {
      "style": 1
    }
  },
  {
    "source": "5ef2ec930000000001005fe2",
    "target": "66d6aedc000000001e00f94d",
    "weight": 0.74,
    "types": {
      "style": 1
    }
  },
  {
    "source": "5b21847911be1079a51a573c",
    "target": "57576ed25e87e7791b68777d",
    "weight": 0.76,
    "types": {
      "style": 1
    }
  },
  {
    "source": "5b21847911be1079a51a573c",
    "target": "5abf90244eacab2c32c7c5e6",
    "weight": 0.73,
    "types": {
      "style": 1
    }
  },
  {
    "source": "57576ed25e87e7791b68777d",
    "target": "586f442550c4b43de8f114b0",
    "weight": 0.77,
    "types": {
      "style": 1
    }
  },
  {
    "source": "5e818a5d0000000001006e10",
    "target": "5abf90244eacab2c32c7c5e6",
    "weight": 0.72,
    "types": {
      "style": 1
    }
  }
];

export const trackClusters: Record<string, string[]> = {
  "中国地理与自然景观": [
    "5ff98b9d0000000001008f40"
  ],
  "硅谷": [
    "57576ed25e87e7791b68777d"
  ],
  "生物鉴定": [
    "5ef2ec930000000001005fe2"
  ],
  "创业招募": [
    "5b21847911be1079a51a573c"
  ],
  "商业分析": [
    "5abf90244eacab2c32c7c5e6"
  ],
  "脑科学与神经科学": [
    "66d6aedc000000001e00f94d"
  ],
  "美国生活": [
    "586f442550c4b43de8f114b0"
  ],
  "就业与职业发展": [
    "5e818a5d0000000001006e10"
  ]
};

export const trendingKeywordGroups: Array<{
  topic: string;
  creators: string[];
  intensity: number;
}> = [];
