/**
 * 将 MediaCrawler 的 creator JSON 数据转换为前端需要的格式
 * 
 * 使用方法：
 * node scripts/convertMediaCrawlerData.js
 */

const fs = require('fs');
const path = require('path');

// 配置路径
const MEDIA_CRAWLER_DATA_DIR = '../../MediaCrawler/data/xhs/creator';
const OUTPUT_FILE = '../src/data/creators.ts';

/**
 * 解析粉丝数字符串（如 "1千+"、"1万+" 等）
 */
function parseFansCount(fansStr) {
  if (!fansStr) return 0;
  
  // 移除 "+" 号
  const str = fansStr.replace('+', '').trim();
  
  if (str.includes('万')) {
    const num = parseFloat(str.replace('万', ''));
    return Math.floor(num * 10000);
  } else if (str.includes('千')) {
    const num = parseFloat(str.replace('千', ''));
    return Math.floor(num * 1000);
  } else {
    return parseInt(str) || 0;
  }
}

/**
 * 从标签中提取主要赛道
 */
function extractPrimaryTrack(tags) {
  if (!tags || !Array.isArray(tags)) return '其他';
  
  // 赛道映射表
  const trackMapping = {
    '美妆': '美妆',
    '时尚': '时尚',
    '穿搭': '时尚',
    '美食': '美食',
    '旅行': '旅行',
    '旅游': '旅行',
    '居家': '居家',
    '家居': '居家',
    '数码': '数码',
    '科技': '数码',
    '母婴': '母婴',
    '亲子': '母婴',
  };
  
  for (const tag of tags) {
    const tagName = tag.name || '';
    for (const [keyword, track] of Object.entries(trackMapping)) {
      if (tagName.includes(keyword)) {
        return track;
      }
    }
  }
  
  return '其他';
}

/**
 * 提取内容形式（从职业标签）
 */
function extractContentForm(tags) {
  if (!tags || !Array.isArray(tags)) return '创作者';
  
  const professionTag = tags.find(tag => tag.tagType === 'profession');
  if (professionTag) {
    return professionTag.name || '创作者';
  }
  
  return '创作者';
}

/**
 * 提取关键词标签
 */
function extractKeywords(tags) {
  if (!tags || !Array.isArray(tags)) return [];
  
  // 过滤掉一些不需要的标签类型，只保留有意义的
  return tags
    .filter(tag => {
      // 排除位置、性别、星座等基础信息
      const name = tag.name || '';
      const excludeKeywords = ['中国', '射手座', '天秤座', '双鱼座', '金牛座', '狮子座', '处女座', '白羊座', '巨蟹座', '摩羯座', '水瓶座', '双子座', '天蝎座'];
      return !excludeKeywords.includes(name) && tag.tagType !== 'location';
    })
    .map(tag => tag.name)
    .filter(name => name && name.length > 0)
    .slice(0, 5); // 最多取 5 个标签
}

/**
 * 转换单个 creator JSON
 */
function convertCreator(filePath, index) {
  const rawData = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  
  // 提取基础信息
  const basicInfo = rawData.basicInfo || {};
  const interactions = rawData.interactions || [];
  const tags = rawData.tags || [];
  
  // 获取粉丝数（通常是第二个 interaction）
  const fansInteraction = interactions.find(item => item.type === 'fans');
  const fansCount = parseFansCount(fansInteraction?.count || '0');
  
  // 提取用户 ID（从文件名）
  const userId = path.basename(filePath, '.json');
  
  return {
    id: userId,
    name: basicInfo.nickname || '未知创作者',
    followers: fansCount,
    engagementIndex: Math.floor(50 + Math.random() * 40), // 暂时用随机数，后续可以计算
    primaryTrack: extractPrimaryTrack(tags),
    contentForm: extractContentForm(tags),
    recentKeywords: extractKeywords(tags), // 从 tags 中提取关键词
    position: { 
      x: (index % 4) * 25 + 10, // 简单的网格布局
      y: Math.floor(index / 4) * 25 + 10 
    },
    // 额外信息（可选）
    avatar: basicInfo.images || basicInfo.imageb || '',
    ipLocation: basicInfo.ipLocation || '',
    desc: basicInfo.desc || '',
    redId: basicInfo.redId || '',
  };
}

/**
 * 生成伪造的边数据（creator 关系）
 */
function generateMockEdges(creators) {
  const edges = [];
  
  // 简单策略：相同赛道的 creator 之间随机生成连接
  for (let i = 0; i < creators.length; i++) {
    for (let j = i + 1; j < creators.length; j++) {
      const creator1 = creators[i];
      const creator2 = creators[j];
      
      // 相同赛道的概率更高
      const samePrimaryTrack = creator1.primaryTrack === creator2.primaryTrack;
      const shouldConnect = samePrimaryTrack 
        ? Math.random() > 0.4  // 60% 概率连接
        : Math.random() > 0.8; // 20% 概率连接
      
      if (shouldConnect) {
        const weight = 0.3 + Math.random() * 0.5; // 0.3-0.8
        edges.push({
          source: creator1.id,
          target: creator2.id,
          weight: parseFloat(weight.toFixed(2)),
          types: {
            keyword: Math.floor(Math.random() * 5),
            audience: Math.floor(Math.random() * 5),
            style: Math.floor(Math.random() * 3),
          },
        });
      }
    }
  }
  
  return edges;
}

/**
 * 生成 TypeScript 文件内容
 */
function generateTypeScriptFile(creators, edges) {
  // 提取所有唯一的赛道
  const allTracks = [...new Set(creators.map(c => c.primaryTrack))];
  
  // 生成 trackClusters
  const trackClusters = {};
  allTracks.forEach(track => {
    trackClusters[track] = creators
      .filter(c => c.primaryTrack === track)
      .map(c => c.id);
  });
  
  const content = `// 此文件由脚本自动生成
// 生成时间: ${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}
// 数据来源: MediaCrawler/data/xhs/creator

export interface CreatorNode {
  id: string;
  name: string;
  followers: number;
  engagementIndex: number;
  primaryTrack: string;
  contentForm: string;
  recentKeywords: string[];
  position: { x: number; y: number };
  // 额外字段
  avatar?: string;
  ipLocation?: string;
  desc?: string;
  redId?: string;
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

export const creators: CreatorNode[] = ${JSON.stringify(creators, null, 2)};

export const creatorEdges: CreatorEdge[] = ${JSON.stringify(edges, null, 2)};

export const trackClusters: Record<string, string[]> = ${JSON.stringify(trackClusters, null, 2)};

export const trendingKeywordGroups: Array<{
  topic: string;
  creators: string[];
  intensity: number;
}> = [
  // 暂时为空，后续从笔记数据中分析生成
];
`;
  
  return content;
}

/**
 * 主函数
 */
function main() {
  console.log('🚀 开始转换 MediaCrawler 数据...\n');
  
  // 读取所有 creator JSON 文件
  const dataDir = path.resolve(__dirname, MEDIA_CRAWLER_DATA_DIR);
  console.log(`📂 数据目录: ${dataDir}`);
  
  const files = fs.readdirSync(dataDir)
    .filter(file => file.endsWith('.json'))
    .map(file => path.join(dataDir, file));
  
  console.log(`📝 找到 ${files.length} 个 creator 文件\n`);
  
  // 转换所有 creator
  const creators = files.map((file, index) => {
    const creator = convertCreator(file, index);
    console.log(`✅ [${index + 1}/${files.length}] ${creator.name} (${creator.primaryTrack}) - ${creator.followers.toLocaleString()} 粉丝`);
    return creator;
  });
  
  console.log('\n🔗 生成关系边...');
  const edges = generateMockEdges(creators);
  console.log(`✅ 生成了 ${edges.length} 条连接\n`);
  
  // 生成 trackClusters
  const allTracks = [...new Set(creators.map(c => c.primaryTrack))];
  const trackClusters = {};
  allTracks.forEach(track => {
    trackClusters[track] = creators
      .filter(c => c.primaryTrack === track)
      .map(c => c.id);
  });
  
  // 生成 TypeScript 文件
  const outputPath = path.resolve(__dirname, OUTPUT_FILE);
  const tsContent = generateTypeScriptFile(creators, edges);
  
  fs.writeFileSync(outputPath, tsContent, 'utf-8');
  console.log(`✅ 数据已写入: ${outputPath}\n`);
  
  // 统计信息
  console.log('📊 统计信息:');
  console.log(`   - 创作者数量: ${creators.length}`);
  console.log(`   - 关系边数量: ${edges.length}`);
  console.log(`   - 赛道数量: ${Object.keys(trackClusters).length}`);
  
  const trackStats = {};
  creators.forEach(c => {
    trackStats[c.primaryTrack] = (trackStats[c.primaryTrack] || 0) + 1;
  });
  console.log('   - 赛道分布:');
  Object.entries(trackStats).forEach(([track, count]) => {
    console.log(`      ${track}: ${count} 人`);
  });
  
  console.log('\n🎉 转换完成！');
}

// 执行
main();
