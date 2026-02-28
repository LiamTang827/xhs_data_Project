"""
成长路径服务 - 基于竞品分析生成内容建议
分析竞品爆款笔记，找出"他们做了但我没做"的内容方向
"""
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime

from database.connection import get_database
from core.llm_gateway import LLMGateway


class GrowthPathService:
    """成长路径分析服务"""
    
    def __init__(self):
        self.db = get_database()
        self.llm = LLMGateway()
    
    def _build_index_series_from_snapshots(self, user_id: str) -> List[Dict]:
        """
        从 user_snapshots.notes 构建 index_series 格式数据
        当 user_profiles.stats.index_series 为空时作为回退
        """
        snapshot = self.db.user_snapshots.find_one(
            {'user_id': user_id},
            {'notes': 1}
        )
        if not snapshot or not snapshot.get('notes'):
            return []
        
        index_series = []
        for note in snapshot['notes']:
            likes = note.get('likes', 0) or 0
            collected = note.get('collected_count', 0) or 0
            comments = note.get('comments_count', 0) or 0
            shares = note.get('share_count', 0) or 0
            
            engagement_count = likes + collected * 2 + comments * 3 + shares * 4
            engagement_index = engagement_count / 1000.0
            
            index_series.append({
                'ts': (note.get('create_time', 0) or 0) * 1000,  # 转为毫秒时间戳与 index_series 格式一致
                'value': round(engagement_index, 2),
                'note_id': note.get('id', note.get('cursor', '')),
                'title': note.get('title', note.get('display_title', ''))
            })
        
        return index_series
    
    async def analyze_growth_opportunities(
        self,
        my_user_id: str,
        competitor_user_id: str,
        top_n: int = 5,
        min_engagement_index: float = 1.0,  # 至少1000互动数
        days: Optional[int] = None  # 只看最近N天的笔记
    ) -> Dict[str, Any]:
        """
        分析成长机会：找出竞品爆款中我可以借鉴的内容
        
        Args:
            my_user_id: 我的用户ID
            competitor_user_id: 竞品用户ID
            top_n: 返回前N个建议
            min_engagement_index: 最小互动指数（筛选爆款）
        
        Returns:
            {
                'my_profile': {...},
                'competitor_profile': {...},
                'opportunities': [
                    {
                        'note_title': '笔记标题',
                        'engagement_index': 10.5,
                        'similarity_to_me': 0.3,  # 低相似度=内容差异大
                        'reason': '这是你还没涉足的领域',
                        'suggestion': 'DeepSeek生成的创作建议'
                    }
                ],
                'summary': 'LLM生成的总结'
            }
        """
        # 1. 获取我的profile和embedding
        my_profile = self.db.user_profiles.find_one({
            'user_id': my_user_id,
            'platform': 'xiaohongshu'
        })
        if not my_profile:
            raise ValueError(f"用户 {my_user_id} 不存在")
        
        my_embedding_doc = self.db.user_embeddings.find_one({
            'user_id': my_user_id,
            'platform': 'xiaohongshu',
            'dimension': 512
        })
        
        if not my_embedding_doc:
            raise ValueError(f"用户 {my_user_id} 没有embedding向量")
        
        my_embedding = np.array(my_embedding_doc['embedding'])
        my_nickname = my_profile.get('basic_info', {}).get('nickname', my_user_id[:16])
        my_topics = my_profile.get('content_info', {}).get('content_topics', [])
        
        # 2. 获取竞品的profile和indexSeries
        competitor_profile = self.db.user_profiles.find_one({
            'user_id': competitor_user_id,
            'platform': 'xiaohongshu'
        })
        if not competitor_profile:
            raise ValueError(f"竞品用户 {competitor_user_id} 不存在")
        
        competitor_nickname = competitor_profile.get('basic_info', {}).get('nickname', competitor_user_id[:16])
        competitor_topics = competitor_profile.get('content_info', {}).get('content_topics', [])
        stats = competitor_profile.get('stats', {})
        index_series = stats.get('index_series', [])
        
        # 如果 index_series 为空，从 user_snapshots.notes 回退读取
        if not index_series:
            index_series = self._build_index_series_from_snapshots(competitor_user_id)
        
        if not index_series:
            raise ValueError(f"竞品用户 {competitor_nickname} 没有笔记数据")
        
        # 3. 按时间范围筛选
        if days:
            cutoff_ms = int((datetime.now().timestamp() - days * 86400) * 1000)
            index_series = [n for n in index_series if (n.get('ts', 0) or 0) >= cutoff_ms]
        
        # 4. 筛选竞品爆款笔记（按互动指数排序）
        hot_notes = [
            note for note in index_series 
            if note.get('value', 0) >= min_engagement_index
        ]
        hot_notes.sort(key=lambda x: x.get('value', 0), reverse=True)
        
        if not hot_notes:
            return {
                'my_profile': {
                    'nickname': my_nickname,
                    'topics': my_topics
                },
                'competitor_profile': {
                    'nickname': competitor_nickname,
                    'topics': competitor_topics
                },
                'opportunities': [],
                'summary': f"{competitor_nickname} 最近没有超过互动指数 {min_engagement_index} 的爆款笔记"
            }
        
        # 4. 获取竞品的embedding（用于计算相似度）
        competitor_embedding_doc = self.db.user_embeddings.find_one({
            'user_id': competitor_user_id,
            'platform': 'xiaohongshu',
            'dimension': 512
        })
        
        # 5. 计算内容差异度
        # 如果没有竞品embedding，使用话题相似度作为备选
        if competitor_embedding_doc:
            competitor_embedding = np.array(competitor_embedding_doc['embedding'])
            # 低相似度 = 内容差异大 = 我还没做的方向
            similarity = float(np.dot(my_embedding, competitor_embedding))
        else:
            # 基于topic overlap计算相似度
            my_topic_set = set(my_topics)
            competitor_topic_set = set(competitor_topics)
            if my_topic_set and competitor_topic_set:
                overlap = len(my_topic_set & competitor_topic_set)
                similarity = overlap / len(my_topic_set | competitor_topic_set)
            else:
                similarity = 0.0
        
        # 6. 选择差异化机会（爆款 + 与我风格有距离）
        opportunities = []
        for note in hot_notes[:top_n * 2]:  # 多取一些用于筛选
            # 相似度决策：中低相似度最佳（太低=完全不相关，太高=已经在做）
            note_data = {
                'note_title': note.get('title', 'N/A'),
                'note_id': note.get('note_id', ''),
                'engagement_index': note.get('value', 0),
                'timestamp': note.get('ts', 0),
                'similarity_to_me': similarity,  # 简化版：用整体相似度
                'engagement_count': int(note.get('value', 0) * 1000)  # 估算互动数
            }
            opportunities.append(note_data)
        
        # 按互动指数排序，取top_n
        opportunities = opportunities[:top_n]
        
        # 7. 调用LLM生成创作建议
        llm_opportunities = await self._generate_content_suggestions(
            my_nickname=my_nickname,
            my_topics=my_topics,
            competitor_nickname=competitor_nickname,
            opportunities=opportunities,
            overall_similarity=similarity
        )
        
        # 8. 生成总结
        summary = await self._generate_summary(
            my_nickname=my_nickname,
            competitor_nickname=competitor_nickname,
            opportunities=llm_opportunities,
            overall_similarity=similarity
        )
        
        return {
            'my_profile': {
                'user_id': my_user_id,
                'nickname': my_nickname,
                'topics': my_topics[:5]
            },
            'competitor_profile': {
                'user_id': competitor_user_id,
                'nickname': competitor_nickname,
                'topics': competitor_topics[:5],
                'total_hot_notes': len(hot_notes)
            },
            'overall_similarity': round(similarity, 3),
            'opportunities': llm_opportunities,
            'summary': summary
        }
    
    async def _generate_content_suggestions(
        self,
        my_nickname: str,
        my_topics: List[str],
        competitor_nickname: str,
        opportunities: List[Dict],
        overall_similarity: float
    ) -> List[Dict[str, Any]]:
        """为每个机会生成创作建议"""
        
        # 构建prompt
        my_topics_str = "、".join(my_topics[:5]) if my_topics else "综合内容"
        
        opportunities_text = "\n".join([
            f"{i+1}. {opp['note_title']} (互动指数: {opp['engagement_index']}, 约{opp['engagement_count']:,}互动)"
            for i, opp in enumerate(opportunities)
        ])
        
        prompt = f"""你是一个小红书内容策略专家。请分析竞品爆款笔记，为创作者提供差异化内容建议。

**我的信息：**
- 昵称：{my_nickname}
- 内容方向：{my_topics_str}

**竞品信息：**
- 昵称：{competitor_nickname}
- 与我的整体相似度：{overall_similarity:.2f} (0=完全不同, 1=非常相似)

**竞品爆款笔记列表：**
{opportunities_text}

**任务：**
为每个爆款笔记生成创作建议，帮助 {my_nickname} 在保持自己风格的基础上，借鉴这些成功经验。

对于每个笔记，输出：
1. **为什么这是机会**：这个笔记为什么值得借鉴？
2. **内容方向建议**：结合我的风格，可以做什么相关内容？
3. **创作角度**：具体可以从哪些角度切入？

输出格式（严格JSON数组）：
[
  {{
    "note_index": 1,
    "reason": "这个笔记抓住了...",
    "direction": "你可以结合你的{my_topics_str}方向...",
    "angles": ["角度1", "角度2", "角度3"]
  }},
  ...
]

只返回JSON数组，不要其他文字。"""
        
        try:
            response = await self.llm.chat(
                prompt=prompt,
                model="deepseek-chat",
                temperature=0.7,
                max_tokens=2000
            )
            
            # 解析JSON响应
            import json
            suggestions = json.loads(response)
            
            # 合并到opportunities
            for i, opp in enumerate(opportunities):
                if i < len(suggestions):
                    sugg = suggestions[i]
                    opp['reason'] = sugg.get('reason', '')
                    opp['direction'] = sugg.get('direction', '')
                    opp['angles'] = sugg.get('angles', [])
                else:
                    opp['reason'] = '待分析'
                    opp['direction'] = ''
                    opp['angles'] = []
            
            return opportunities
            
        except Exception as e:
            print(f"LLM生成建议失败: {e}")
            # 降级：返回基础信息
            for opp in opportunities:
                opp['reason'] = '这是竞品的爆款内容，值得研究'
                opp['direction'] = f'结合你的{my_topics_str}方向进行创作'
                opp['angles'] = ['保持个人风格', '参考数据表现', '创新表达方式']
            return opportunities
    
    async def _generate_summary(
        self,
        my_nickname: str,
        competitor_nickname: str,
        opportunities: List[Dict],
        overall_similarity: float
    ) -> str:
        """生成总体策略建议"""
        
        if not opportunities:
            return f"{competitor_nickname} 目前没有足够的爆款内容可供参考"
        
        avg_engagement = sum(o['engagement_index'] for o in opportunities) / len(opportunities)
        
        prompt = f"""基于以下分析结果，为 {my_nickname} 生成一段简洁的成长路径建议（100字以内）：

- 竞品：{competitor_nickname}
- 内容相似度：{overall_similarity:.2f}
- 竞品爆款数量：{len(opportunities)}
- 平均互动指数：{avg_engagement:.1f}

建议重点：
1. 总体策略（是深度学习还是差异化？）
2. 最值得借鉴的1-2个方向
3. 如何保持个人特色

用鼓励、实用的语气，直接给出行动建议。"""
        
        try:
            summary = await self.llm.chat(
                prompt=prompt,
                model="deepseek-chat",
                temperature=0.7,
                max_tokens=200
            )
            return summary.strip()
        except Exception as e:
            print(f"LLM生成总结失败: {e}")
            return f"发现 {len(opportunities)} 个值得借鉴的爆款方向，建议结合自己的风格进行差异化创作"
