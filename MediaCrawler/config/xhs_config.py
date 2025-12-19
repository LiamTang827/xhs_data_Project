# -*- coding: utf-8 -*-
# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。


# 小红书平台配置

# 排序方式，具体的枚举值在media_platform/xhs/field.py中
SORT_TYPE = "popularity_descending"

# Only get creator info, not notes
XHS_ONLY_GET_CREATOR_INFO = False   

# 指定笔记URL列表, 必须要携带xsec_token参数
XHS_SPECIFIED_NOTE_URL_LIST = [
    "https://www.xiaohongshu.com/explore/69069bdf000000000301016a?xsec_token=ABh5cTCvUkZHfI2UJ2hf5MK8l31Qe1ULk3Q3FsIkUleaY=&xsec_source=pc_user",
]

# 指定创作者URL列表 (支持完整URL或纯ID)
# 支持格式:
# 1. 完整创作者主页URL (带xsec_token和xsec_source参数): "https://www.xiaohongshu.com/user/profile/5eb8e1d400000000010075ae?xsec_token=AB1nWBKCo1vE2HEkfoJUOi5B6BE5n7wVrbdpHoWIj5xHw=&xsec_source=pc_feed"
# 2. 纯user_id: "63e36c9a000000002703502b"
XHS_CREATOR_ID_LIST = [
    "https://www.xiaohongshu.com/user/profile/5ff98b9d0000000001008f40?xsec_token=ABfPMaJiGlsCR0UjLUGyeG5id69V0Go07-ATn337_xVfw%3D&xsec_source=pc_search",
    "https://www.xiaohongshu.com/user/profile/5ef2ec930000000001005fe2?xsec_token=AB5Pg6ITMZLaJyswEYk9kTwYjcwH3pDgDamo3b0ocS_G4%3D&xsec_source=pc_search",
    "https://www.xiaohongshu.com/user/profile/5abf90244eacab2c32c7c5e6?xsec_token=ABsg5_UfOD-capApvX8n4kQAvrEvyMo3CziEuxqQmbj3Y%3D&xsec_source=pc_search",
    "https://www.xiaohongshu.com/user/profile/5e818a5d0000000001006e10?xsec_token=ABo0txQU1lWfQNBVP971OWbPhyBs2jFb9zr3HZRs4sAt0%3D&xsec_source=pc_search",
    "https://www.xiaohongshu.com/user/profile/5ff98b9d0000000001008f40?xsec_token=ABfPMaJiGlsCR0UjLUGyeG5id69V0Go07-ATn337_xVfw%3D&xsec_source=pc_search",
    "https://www.xiaohongshu.com/user/profile/66d6aedc000000001e00f94d?xsec_token=ABXKSJhuGJzZyIggNsg08UAE8WjpmJTWt3iXyhtPQSWWs%3D&xsec_source=pc_search"
    ]
