// 此文件由脚本自动生成
// 生成时间: 2025/11/19 21:02:42
// 数据来源: data-analysiter/snapshots

export interface CreatorNode {
  id: string;
  name: string;
  followers: number;
  engagementIndex: number;
  primaryTrack: string;
  contentForm: string;
  recentKeywords: string[];
  position: { x: number; y: number };
  avatar?: string;
  ipLocation?: string;
  desc?: string;
  redId?: string;
  followersDelta?: number;
  interactionDelta?: number;
  indexSeries?: Array<{ time: string; followers: number; interaction: number; influence: number }>;
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
    "followers": 1105057,
    "engagementIndex": 3658603,
    "primaryTrack": "其他",
    "contentForm": "",
    "recentKeywords": [],
    "position": {
      "x": 0,
      "y": 0
    },
    "avatar": "https://sns-avatar-qc.xhscdn.com/avatar/1040g2jo31c2kka15h0005nvpheeg93q0419vqv8?imageView2/2/w/360/format/webp",
    "ipLocation": "北京",
    "desc": "热爱人类，热爱地球。",
    "followersDelta": 100000,
    "interactionDelta": 300000,
    "indexSeriesRaw": [
      {
        "time": "2025-11-17T19:00:34",
        "followers": 1005057,
        "interaction": 3358603,
        "influence": 1946475,
        "ts": 1763377234000,
        "value": 1946475
      },
      {
        "time": "2025-11-19T11:14:44",
        "followers": 1105057,
        "interaction": 3658603,
        "influence": 2126475,
        "ts": 1763522084000,
        "value": 2126475
      }
    ],
    "indexSeries": [
      {
        "ts": 1763377234000,
        "value": 1946475
      },
      {
        "ts": 1763522084000,
        "value": 2126475
      }
    ]
  },
  {
    "id": "5ef2ec930000000001005fe2",
    "name": "无穷小亮的科普日常",
    "followers": 1709650,
    "engagementIndex": 4884914,
    "primaryTrack": "其他",
    "contentForm": "",
    "recentKeywords": [],
    "position": {
      "x": 0,
      "y": 0
    },
    "avatar": "https://sns-avatar-qc.xhscdn.com/avatar/5fcf402a1a696e0001b66522.jpg?imageView2/2/w/360/format/webp",
    "ipLocation": "北京",
    "desc": "《博物》杂志副主编，《中国国家地理》融媒体中心主任，中国科普作家协会会员，中国农大昆虫学硕士，2017中国科协十大科学传播人物。",
    "followersDelta": 200000,
    "interactionDelta": 400000,
    "indexSeriesRaw": [
      {
        "time": "2025-11-17T19:00:15",
        "followers": 1509650,
        "interaction": 4484914,
        "influence": 2699756,
        "ts": 1763377215000,
        "value": 2699756
      },
      {
        "time": "2025-11-19T11:14:44",
        "followers": 1709650,
        "interaction": 4884914,
        "influence": 2979756,
        "ts": 1763522084000,
        "value": 2979756
      }
    ],
    "indexSeries": [
      {
        "ts": 1763377215000,
        "value": 2699756
      },
      {
        "ts": 1763522084000,
        "value": 2979756
      }
    ]
  },
  {
    "id": "5abf90244eacab2c32c7c5e6",
    "name": "小Lin说",
    "followers": 1984802,
    "engagementIndex": 4203332,
    "primaryTrack": "其他",
    "contentForm": "",
    "recentKeywords": [],
    "position": {
      "x": 0,
      "y": 0
    },
    "avatar": "https://sns-avatar-qc.xhscdn.com/avatar/616ee14936ede13faad1038e.jpg?imageView2/2/w/360/format/webp",
    "ipLocation": "北京",
    "desc": "商业财经不无聊～\n💗北大-＞哥大-＞JPMorgan->创业\n对后期感兴趣的小伙伴可以联系：xiaolin_recruiting@163.com\n‼️无小号，不会以任何方式私信粉丝，谨防受骗~",
    "followersDelta": 100000,
    "interactionDelta": 200000,
    "indexSeriesRaw": [
      {
        "time": "2025-11-17T18:59:53",
        "followers": 1884802,
        "interaction": 4003332,
        "influence": 2732214,
        "ts": 1763377193000,
        "value": 2732214
      },
      {
        "time": "2025-11-19T11:14:45",
        "followers": 1984802,
        "interaction": 4203332,
        "influence": 2872214,
        "ts": 1763522085000,
        "value": 2872214
      }
    ],
    "indexSeries": [
      {
        "ts": 1763377193000,
        "value": 2732214
      },
      {
        "ts": 1763522085000,
        "value": 2872214
      }
    ]
  },
  {
    "id": "5e818a5d0000000001006e10",
    "name": "所长林超",
    "followers": 1318568,
    "engagementIndex": 2498656,
    "primaryTrack": "其他",
    "contentForm": "",
    "recentKeywords": [],
    "position": {
      "x": 0,
      "y": 0
    },
    "avatar": "https://sns-avatar-qc.xhscdn.com/avatar/63907ba4ead25995c5dd9dfb.jpg?imageView2/2/w/360/format/webp",
    "ipLocation": "",
    "desc": "《跨学科通识课》及新书《开窍》已上线\n薛定谔的眨眼，看科技&商业原理",
    "followersDelta": 200000,
    "interactionDelta": 50000,
    "indexSeriesRaw": [
      {
        "time": "2025-11-17T18:58:19",
        "followers": 1118568,
        "interaction": 2448656,
        "influence": 1650603,
        "ts": 1763377099000,
        "value": 1650603
      },
      {
        "time": "2025-11-19T11:14:46",
        "followers": 1318568,
        "interaction": 2498656,
        "influence": 1790603,
        "ts": 1763522086000,
        "value": 1790603
      }
    ],
    "indexSeries": [
      {
        "ts": 1763377099000,
        "value": 1650603
      },
      {
        "ts": 1763522086000,
        "value": 1790603
      }
    ]
  },
  {
    "id": "66d6aedc000000001e00f94d",
    "name": "大圆镜科普",
    "followers": 28048,
    "engagementIndex": 146119,
    "primaryTrack": "其他",
    "contentForm": "",
    "recentKeywords": [],
    "position": {
      "x": 0,
      "y": 0
    },
    "avatar": "https://sns-avatar-qc.xhscdn.com/avatar/1040g2jo31k07dtepj46g5pmmlre7huadb3030a8?imageView2/2/w/360/format/webp",
    "ipLocation": "上海",
    "desc": "科技之大，艺术之圆，哲学之镜\n天桥脑科学研究院大圆镜工作室“用AI做最好的视频”\n（每周六日双更）",
    "followersDelta": 1000,
    "interactionDelta": 10000,
    "indexSeriesRaw": [
      {
        "time": "2025-11-17T18:49:45",
        "followers": 27048,
        "interaction": 136119,
        "influence": 70676,
        "ts": 1763376585000,
        "value": 70676
      },
      {
        "time": "2025-11-19T11:14:46",
        "followers": 28048,
        "interaction": 146119,
        "influence": 75276,
        "ts": 1763522086000,
        "value": 75276
      }
    ],
    "indexSeries": [
      {
        "ts": 1763376585000,
        "value": 70676
      },
      {
        "ts": 1763522086000,
        "value": 75276
      }
    ]
  }
];

export const creatorEdges: CreatorEdge[] = [];

export const trackClusters: Record<string, string[]> = {
  "其他": [
    "5ff98b9d0000000001008f40",
    "5ef2ec930000000001005fe2",
    "5abf90244eacab2c32c7c5e6",
    "5e818a5d0000000001006e10",
    "66d6aedc000000001e00f94d"
  ]
};

export const trendingKeywordGroups: Array<{
  topic: string;
  creators: string[];
  intensity: number;
}> = [];
