/**
 * 将 TrendRadar 的 txt 热搜数据转换为前端 trending.ts
 * 用法：node scripts/convertTxtTrendingData.js
 */

const fs = require('fs');
const path = require('path');

const TXT_FILE = '../../TrendRadar/output/2025年11月14日/txt/22时24分.txt';
const OUTPUT_FILE = '../src/data/trending.ts';
const CREATORS_DATA_FILE = '../src/data/creators.ts';

function getCompetitionLevel(rank) {
  if (rank <= 5) return '高';
  if (rank <= 15) return '中';
  return '低';
}

function generateSuggestedAngles(topic) {
  const templates = [
    `如何快速参与“${topic}”话题？`,
    `普通人也能聊“${topic}”的3个角度`,
    `“${topic}”背后的社会现象分析`,
    `我的“${topic}”真实体验`,
    `“${topic}”值得关注的原因`,
  ];
  return templates.sort(() => 0.5 - Math.random()).slice(0, 2);
}

function main() {
  // 读取创作者ID
  let creatorIds = [];
  const creatorsPath = path.resolve(__dirname, CREATORS_DATA_FILE);
  if (fs.existsSync(creatorsPath)) {
    const creatorsContent = fs.readFileSync(creatorsPath, 'utf-8');
    const idsMatch = creatorsContent.match(/id: "([^"]+)"/g);
    if (idsMatch) {
      creatorIds = idsMatch.map(idStr => idStr.replace('id: "', '').replace('"', ''));
    }
  }

  // 读取txt
  const txtPath = path.resolve(__dirname, TXT_FILE);
  const lines = fs.readFileSync(txtPath, 'utf-8').split(/\r?\n/);

  const trendingData = [];
  let currentPlatform = '';
  let topicCount = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    // 平台行
    if (/^[a-zA-Z0-9\-]+ \| /.test(line)) {
      currentPlatform = line.split('|')[1].trim();
      topicCount = 0;
      continue;
    }
    // 话题行
    const match = line.match(/^(\d+)\.\s*(.+?)(?:\s*\[URL:.*?\])?/);
    if (match) {
      topicCount++;
      if (topicCount > 10) continue; // 每个平台只取前10
      const rank = parseInt(match[1], 10);
      const topic = match[2].replace(/\s+$/, '');
      // 随机分配1-3个creator
      const creators = creatorIds.length > 0 ? [...creatorIds].sort(() => 0.5 - Math.random()).slice(0, Math.floor(1 + Math.random() * 3)) : [];
      trendingData.push({
        topic: `${currentPlatform} | ${topic}`,
        heatScore: 95 - (rank - 1) * 4 + Math.floor(Math.random() * 3),
        creators,
        avgViews: `${(Math.random() * 8 + 2).toFixed(1)}w`,
        growthRate: `+${(10 + Math.random() * 40).toFixed(1)}%`,
        competitionLevel: getCompetitionLevel(rank),
        suggestedAngles: generateSuggestedAngles(topic),
      });
    }
  }

  // 只取前30个
  const sortedData = trendingData.slice(0, 5);

  // 输出ts
  const content = `// 此文件由脚本自动生成\n// 数据来源: TrendRadar/txt/22时24分.txt\n\nexport interface TrendingTopic {\n  topic: string;\n  heatScore: number;\n  creators: string[];\n  avgViews: string;\n  growthRate: string;\n  competitionLevel: \"低\" | \"中\" | \"高\";\n  suggestedAngles: string[];\n}\n\nexport const trendingTopicsData: TrendingTopic[] = ${JSON.stringify(sortedData, null, 2)};\n`;
  fs.writeFileSync(path.resolve(__dirname, OUTPUT_FILE), content, 'utf-8');
  console.log(`✅ trending.ts 已生成, 共${sortedData.length}条`);
}

main();
