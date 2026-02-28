#!/usr/bin/env python3
"""
添加多个prompt模板到数据库
支持不同的内容生成风格
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import StylePromptRepository

# 定义多个prompt模板
PROMPT_TEMPLATES = [
    {
        "platform": "xiaohongshu",
        "prompt_type": "style_generation",
        "template_id": "default",  # 默认模板
        "name": "通用风格模仿",
        "template": """你是一位经验丰富的小红书内容创作者，擅长模仿不同博主的风格进行创作。

【被模仿者档案】
昵称：{nickname}
内容主题：{topics}
内容风格：{content_style}
价值点：{value_points}

【参考笔记】（以下是该博主的典型笔记）
{sample_notes}

【任务】
请以这位博主的风格，为主题"{user_topic}"创作一篇小红书笔记。

【要求】
1. 文案风格要高度贴近该博主的特点
2. 保持该博主常用的表达方式和语气
3. 体现该博主的价值观和内容侧重点
4. 标题要吸引人，正文要有亮点
5. 适当添加emoji增加活力
6. 最后给出3-5个相关话题标签

【输出格式】
标题：[在这里输出标题]

正文：
[在这里输出正文内容]

话题标签：
#标签1 #标签2 #标签3
""",
        "variables": ["nickname", "topics", "content_style", "value_points", "sample_notes", "user_topic"],
        "description": "通用的风格模仿模板，适合各种类型的内容创作",
        "use_cases": ["日常分享", "Vlog", "生活记录"],
        "example_output": "标题清晰、正文完整、包含话题标签"
    },
    
    {
        "platform": "xiaohongshu",
        "prompt_type": "style_generation",
        "template_id": "planting",  # 种草推荐型
        "name": "种草推荐型",
        "template": """你是一位擅长种草推荐的小红书博主，现在要模仿{nickname}的风格创作种草内容。

【被模仿者特征】
- 主要话题：{topics}
- 内容风格：{content_style}
- 核心价值：{value_points}

【参考笔记风格】
{sample_notes}

【创作任务】
为"{user_topic}"创作一篇**种草推荐型**笔记。

【创作要点】
1. 🎯 开头要有Hook：用痛点/场景/惊喜开场
2. 💎 产品亮点：突出2-3个核心卖点
3. 📊 真实体验：加入具体使用感受和数据
4. ✨ 情绪渲染：用形容词和emoji增强感染力
5. 🏷️ 价格信息：适当提及性价比（如果相关）
6. 🔖 行动召唤：引导收藏/点赞/购买

【输出格式】
标题：[8-15字，包含数字或符号吸引眼球]

正文：
【开场Hook】
[1-2句话，引发共鸣或好奇]

【产品介绍】
[详细描述产品特点]

【使用体验】
[真实感受和细节]

【总结推荐】
[最后点评和购买建议]

话题标签：#种草 #推荐 #[相关话题]
""",
        "variables": ["nickname", "topics", "content_style", "value_points", "sample_notes", "user_topic"],
        "description": "专门用于产品、好物推荐的种草型模板",
        "use_cases": ["产品测评", "好物分享", "购物推荐", "探店"],
        "example_output": "强调产品亮点和使用体验，情绪渲染力强"
    },
    
    {
        "platform": "xiaohongshu",
        "prompt_type": "style_generation",
        "template_id": "tutorial",  # 干货教程型
        "name": "干货教程型",
        "template": """你是一位知识分享类博主，要模仿{nickname}的风格创作干货教程。

【被模仿者特征】
- 内容领域：{topics}
- 表达风格：{content_style}
- 知识价值：{value_points}

【参考内容】
{sample_notes}

【创作任务】
为"{user_topic}"创作一篇**干货教程型**笔记。

【结构要求】
1. 📌 标题：数字+关键词（如"5个技巧"、"3步搞定"）
2. 🎯 开场：说明学会这个能解决什么问题
3. 📝 步骤拆解：分点列举，每点有小标题
4. 💡 注意事项：提醒容易踩的坑
5. 🎁 福利彩蛋：额外的小技巧或资源
6. 🔗 话题标签：含"干货"、"教程"等关键词

【写作风格】
- 逻辑清晰：一二三四，条理分明
- 简洁实用：直接给方法，少讲理论
- 通俗易懂：避免专业术语，用大白话
- 可操作性：读完就能照着做

【输出格式】
标题：[数字+动词+关键词，如"7天学会XXX"]

开场：
[为什么要学这个？解决什么问题？]

方法步骤：
第一步：[小标题]
[具体操作]

第二步：[小标题]
[具体操作]

...

注意事项：
⚠️ [容易出错的地方]

话题标签：#干货分享 #教程 #技巧
""",
        "variables": ["nickname", "topics", "content_style", "value_points", "sample_notes", "user_topic"],
        "description": "适合知识分享、技巧教学的干货型模板",
        "use_cases": ["技能教程", "方法论", "攻略指南", "知识科普"],
        "example_output": "结构化强，步骤清晰，实操性强"
    },
    
    {
        "platform": "xiaohongshu",
        "prompt_type": "style_generation",
        "template_id": "story",  # 情感故事型
        "name": "情感故事型",
        "template": """你是一位善于讲故事的小红书博主，要模仿{nickname}的风格创作情感内容。

【被模仿者特征】
- 内容主题：{topics}
- 叙事风格：{content_style}
- 情感共鸣点：{value_points}

【参考笔记】
{sample_notes}

【创作任务】
围绕"{user_topic}"创作一篇**情感故事型**笔记。

【叙事结构】
1. 🎬 开场设定：时间、地点、人物、事件
2. 💭 情感铺垫：描述心情和内心活动
3. 📖 故事展开：具体情节，有起承转合
4. 💡 感悟升华：从故事中得到的启发
5. 🤝 共鸣收尾：引发读者思考或共鸣

【写作技巧】
- 细节刻画：用具体的场景和对话
- 情绪真实：不做作，不矫情
- 节奏把控：该慢的地方慢，该快的地方快
- 留白艺术：不说满，给读者想象空间
- emoji使用：恰到好处，不要太多

【输出格式】
标题：[情感词+场景/人物，如"那一刻我突然懂了"]

正文：
[自然的故事叙述，像和朋友聊天一样]

[适当分段，每段2-3句话]

[用对话或心理描写增强代入感]

[最后升华主题，引发思考]

话题标签：#故事 #情感 #感悟
""",
        "variables": ["nickname", "topics", "content_style", "value_points", "sample_notes", "user_topic"],
        "description": "适合情感分享、故事叙述的内容类型",
        "use_cases": ["情感故事", "人生感悟", "成长经历", "生活碎片"],
        "example_output": "故事性强，情感真挚，引发共鸣"
    },
    
    {
        "platform": "xiaohongshu",
        "prompt_type": "style_generation",
        "template_id": "trendy",  # 潮流热点型
        "name": "潮流热点型",
        "template": """你是一位善于追热点的小红书博主，要模仿{nickname}的风格创作热点内容。

【被模仿者特征】
- 内容领域：{topics}
- 风格特点：{content_style}
- 核心优势：{value_points}

【参考内容】
{sample_notes}

【创作任务】
结合"{user_topic}"创作一篇**蹭热点型**笔记。

【热点结合要点】
1. 🔥 热点名称：开头直接点明热点
2. 🤔 新角度：找到独特的切入点
3. 💬 观点明确：不要中庸，要有立场
4. 📸 可视化：善用符号、换行、emoji
5. 🎯 互动性：设置话题讨论或投票
6. ⏰ 时效性：尽快发布，抓住流量窗口

【内容结构】
- 开篇点题：一句话说清楚在蹭什么热点
- 观点输出：表达自己的看法（可以有争议）
- 案例支撑：举1-2个例子
- 互动引导：提出问题，引发讨论

【输出格式】
标题：[热点关键词+疑问/数字，如"XXX事件，我有话说"]

开场：
[直接点明热点+快速表态]

观点：
[分点阐述你的看法]

互动：
[提出问题，引导评论]

话题标签：#[热点名称] #热点 #讨论
""",
        "variables": ["nickname", "topics", "content_style", "value_points", "sample_notes", "user_topic"],
        "description": "结合当下热点创作内容，提升流量曝光",
        "use_cases": ["社会热点", "行业新闻", "节日营销", "趋势分析"],
        "example_output": "紧跟热点，观点鲜明，互动性强"
    },
    
    {
        "platform": "general",  # 通用平台，不限于小红书
        "prompt_type": "founder_content",  # 新类型：创始人内容
        "template_id": "founder_personal",
        "name": "创始人个人品牌内容",
        "template": """你是一位顶级创始人个人品牌内容顾问。

请帮我写一条创始人第一人称内容，风格专业、有洞察、有温度，不浮夸、不营销。

一、基础信息
- 创始人姓名：{founder_name}
- 公司名称：{company_name}
- 公司定位（一句话）：{company_positioning}
- 个人背景（教育 / 过往公司 / 行业经历）：{personal_background}
- 当前阶段：{current_stage}
- 目标平台：{target_platform}

二、目标受众
{target_audience}

三、本条内容主题
主题类型：{content_theme}

四、背景信息（尽量具体）
- 时间 / 地点：{time_location}
- 具体事件：{specific_event}
- 关键人物：{key_people}
- 关键数据（如有）：{key_data}
- 特别值得分享的瞬间或洞察：{special_insight}

五、希望强调的核心信息
- 我们解决的核心问题：{core_problem}
- 行业趋势或机会：{industry_trend}
- 我个人的独特视角：{unique_perspective}
- 希望建立的认知：{desired_perception}

六、写作结构要求

1）开头
用具体场景或真实细节切入，不要空话。

2）中段
- 提炼1–2个洞察
- 结合行业趋势或数据
- 展示创始人判断力（不要"我们很兴奋"这类空话）

3）结尾
- 有温度的感谢或思考
- 或一个轻度CTA（欢迎交流 / 招人 / 寻找合作）

七、风格要求
- 语气专业但自然
- 不用夸张词汇
- 不堆砌行业黑话
- 不自卖自夸
- 控制在150–300字（可根据平台调整）
- 避免使用过多emoji（如是LinkedIn可不用）

八、可选增强模块（按需添加）
- 加入1个行业数据增强可信度
- 引用一段对话或现场瞬间
- 加一句长期愿景表达
- 轻微展示创始人个人价值观

【输出要求】
请直接输出文案内容，无需标注"标题"、"正文"等字样。内容应当完整、连贯、自然。
""",
        "variables": [
            "founder_name", "company_name", "company_positioning", "personal_background",
            "current_stage", "target_platform", "target_audience", "content_theme",
            "time_location", "specific_event", "key_people", "key_data", "special_insight",
            "core_problem", "industry_trend", "unique_perspective", "desired_perception"
        ],
        "description": "创始人个人品牌内容生成模板，适用于LinkedIn、Twitter、公众号等多平台",
        "use_cases": ["参会演讲", "产品发布", "融资公告", "行业观点", "创业故事", "团队分享"],
        "example_output": "专业有洞察、有温度但不浮夸的创始人第一人称内容"
    }
]


def add_templates():
    """添加所有模板到数据库"""
    print("=" * 60)
    print("📝 添加多个Prompt模板到数据库")
    print("=" * 60)
    
    prompt_repo = StylePromptRepository()
    
    added = 0
    updated = 0
    skipped = 0
    
    for i, template_data in enumerate(PROMPT_TEMPLATES, 1):
        template_id = template_data["template_id"]
        name = template_data["name"]
        
        print(f"\n[{i}/{len(PROMPT_TEMPLATES)}] 处理模板: {name} (ID: {template_id})")
        
        try:
            # 检查是否已存在相同template_id的模板
            existing = prompt_repo.collection.find_one({
                "platform": template_data["platform"],
                "prompt_type": template_data["prompt_type"],
                "template_id": template_id
            })
            
            if existing:
                # 更新现有模板
                prompt_repo.collection.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {
                        **template_data,
                        "updated_at": datetime.now()
                    }}
                )
                print(f"  ✅ 模板已更新")
                updated += 1
            else:
                # 添加新模板
                template_data["created_at"] = datetime.now()
                template_data["updated_at"] = datetime.now()
                prompt_repo.collection.insert_one(template_data)
                print(f"  ✅ 模板已添加")
                added += 1
                
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            skipped += 1
    
    # 统计
    print("\n" + "=" * 60)
    print("📊 处理完成！")
    print(f"  • 新增: {added} 个")
    print(f"  • 更新: {updated} 个")
    print(f"  • 失败: {skipped} 个")
    print("=" * 60)
    
    # 显示所有模板
    print("\n📋 当前所有模板:")
    all_prompts = list(prompt_repo.collection.find({
        "platform": "xiaohongshu",
        "prompt_type": "style_generation"
    }))
    
    for i, p in enumerate(all_prompts, 1):
        print(f"\n{i}. {p.get('name')} (ID: {p.get('template_id', 'unknown')})")
        print(f"   描述: {p.get('description', '')}")
        print(f"   适用场景: {', '.join(p.get('use_cases', []))}")


if __name__ == "__main__":
    try:
        add_templates()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
