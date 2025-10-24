from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class UserNotesRequest(BaseModel):
    user_url: str = Field(..., description="小红书用户的个人主页URL")
    cookies: str = Field(..., description="用于认证的Cookie字符串")
    proxies: Optional[Dict[str, str]] = None

class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None