from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class CollectRequest(BaseModel):
    platform: Literal["xiaohongshu", "douyin", "bilibili", "youtube", "instagram", "tiktok"]
    url: str = Field(..., description="宣发链接")
    cookie: Optional[str] = Field(None, description="平台Cookie（小红书/抖音星图需要）")
    api_key: Optional[str] = Field(None, description="平台API Key（YouTube等需要）")

class PromotionData(BaseModel):
    platform: str
    url: str
    title: Optional[str] = None
    author: Optional[str] = None
    publish_time: Optional[str] = None

    views: Optional[int] = Field(None, alias="曝光量/播放量")
    reads: Optional[int] = Field(None, alias="阅读量")
    likes: Optional[int] = Field(None, alias="点赞量")
    comments: Optional[int] = Field(None, alias="评论量")
    collects: Optional[int] = Field(None, alias="收藏量")
    shares: Optional[int] = Field(None, alias="转发量/分享量")
    followers: Optional[int] = Field(None, alias="粉丝数")

    engagement_rate: Optional[float] = None
    collect_time: datetime = Field(default_factory=datetime.now)
    status: str = "success"
    error_msg: Optional[str] = None

class APIResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[PromotionData] = None
