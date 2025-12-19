/**
 * 将 TrendRadar 的当日汇总 HTML 数据转换为前端需要的格式
 * 
 * 使用方法：
 * node scripts/convertTrendRadarData.js
 */

const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');

// --- 配置 ---
const TREND_RADAR_HTML_FILE = '../../TrendRadar/output/2025年11月14日/html/当日汇总.html';
const OUTPUT_FILE = '../src/data/trending.ts';
const CREATORS_DATA_FILE = '../src/data/creators.ts'; // 用于关联创作者

// --- 辅助函数 ---

/**
 * 解析热度字符串（如 "热度: 3.4w"）
 */
function parseHeatCount(heatStr) {
  if (!heatStr) return 0;
  const match = heatStr.match(/(\d+(\.\d+)?)[w万]/);
  if (match && match[1]) {
    return parseFloat(match[1]);
  }
  return 0;
}

/**
 * 根据新闻条目数判断竞争等级
 */
function getCompetitionLevel(itemCount) {
  if (itemCount <= 3) return '低';
  if (itemCount <= 6) return '中';
  return '高';
}

/**
 * 生成模拟的建议切入角度
 */
function generateSuggestedAngles(topic) {
  const templates = [
    `分享我用 ${topic} 的真实体验`,
    `普通人如何通过 ${topic} 提升自己`,
    `${topic} 的 N 个隐藏技巧，99%的人不知道`,
    `关于 ${topic}，这些是我的血泪教训`,
  ];
  // a simple shuffle
  return templates.sort(() => 0.5 - Math.random()).slice(0, 2);
}

/**
 * 生成 TypeScript 文件内容
 */
function generateTypeScriptFile(trendingData) {
  const content = `// 此文件由脚本自动生成
// 生成时间: ${new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}
// 数据来源: TrendRadar/output/.../当日汇总.html

export interface TrendingTopic {
  topic: string;
  heatScore: number;
  creators: string[];
  avgViews: string;
  growthRate: string;
  competitionLevel: "低" | "中" | "高";
  suggestedAngles: string[];
}

export const trendingTopicsData: TrendingTopic[] = ${JSON.stringify(trendingData, null, 2)};
`;
  return content;
}


// --- 主函数 ---
function main() {
  console.log('🚀 开始转换 TrendRadar HTML 数据...\n');

  // 读取并解析 HTML 文件
  const htmlPath = path.resolve(__dirname, TREND_RADAR_HTML_FILE);
  if (!fs.existsSync(htmlPath)) {
    console.error(`❌ 错误: HTML 文件未找到于 ${htmlPath}`);
    return;
  }
  console.log(`📄 读取 HTML 文件: ${htmlPath}`);
  const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
  const $ = cheerio.load(htmlContent);

  // 读取创作者数据以进行关联
  const creatorsPath = path.resolve(__dirname, CREATORS_DATA_FILE);
  let creatorIds = [];
  if (fs.existsSync(creatorsPath)) {
    // 注意：这里我们用一个不太优雅但有效的方式来提取ID，避免引入ts-node
    const creatorsContent = fs.readFileSync(creatorsPath, 'utf-8');
    const idsMatch = creatorsContent.match(/id: "([^"]+)"/g);
    if (idsMatch) {
      creatorIds = idsMatch.map(idStr => idStr.replace('id: "', '').replace('"', ''));
    }
    console.log(`🧑‍💻 找到 ${creatorIds.length} 位创作者用于关联`);
  }

  const trendingData = [];

  // 遍历每个热词分组
  $('.word-group').each((i, group) => {
    const topic = $(group).find('.word-name').text().trim();
    if (!topic) return;

    const newsItems = $(group).find('.news-item');
    const itemCount = newsItems.length;
    
    const wordCountText = $(group).find('.word-count').text().trim();
    const heatScore = parseInt(wordCountText.match(/(\d+)/)?.[0] || '0', 10) * 10;

    let maxHeat = 0;
    newsItems.each((j, item) => {
      const heatText = $(item).find('.count-info').text().trim();
      const heat = parseHeatCount(heatText);
      if (heat > maxHeat) {
        maxHeat = heat;
      }
    });

    // 随机关联一些创作者
    const associatedCreators = creatorIds.length > 0 
      ? [...creatorIds].sort(() => 0.5 - Math.random()).slice(0, Math.floor(1 + Math.random() * 3))
      : [];

    trendingData.push({
      topic,
      heatScore: Math.min(95, heatScore), // 最高95分
      creators: associatedCreators,
      avgViews: `${maxHeat.toFixed(1)}w`,
      growthRate: `+${(10 + Math.random() * 40).toFixed(1)}%`,
      competitionLevel: getCompetitionLevel(itemCount),
      suggestedAngles: generateSuggestedAngles(topic),
    });
  });
  
  console.log(`\n📊 成功提取 ${trendingData.length} 个热点话题`);

  // 排序并截取前10个
  const sortedData = trendingData.sort((a, b) => b.heatScore - a.heatScore).slice(0, 10);
  console.log(`🔝 已按热度排序并选取 Top 10\n`);

  // 生成 TypeScript 文件
  const outputPath = path.resolve(__dirname, OUTPUT_FILE);
  const tsContent = generateTypeScriptFile(sortedData);
  fs.writeFileSync(outputPath, tsContent, 'utf-8');
  console.log(`✅ 数据已写入: ${outputPath}\n`);

  console.log('🎉 转换完成！');
}

// 执行
main();
