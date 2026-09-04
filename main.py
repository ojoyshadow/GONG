from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os
import time

from models import CollectRequest, APIResponse, PromotionData
from collectors import (
    XiaoHongShuCollector,
    DouyinXingtuCollector,
    BilibiliCollector,
    YouTubeCollector,
    InstagramCollector,
    TikTokCollector,
)

app = FastAPI(
    title="多平台宣发数据采集API",
    description="支持小红书、抖音、B站、YouTube、Instagram、TikTok的宣发数据自动化采集",
    version="1.0.0"
)

# CORS配置（允许浏览器脚本跨域调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key鉴权
security = HTTPBearer()
API_KEY = os.getenv("API_KEY", "your-secure-api-key-here")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_KEY:
        raise HTTPException(status_code=401, detail="无效的API Key")
    return credentials.credentials

# 采集器工厂
COLLECTORS = {
    "xiaohongshu": lambda req: XiaoHongShuCollector(cookie=req.cookie),
    "douyin": lambda req: DouyinXingtuCollector(cookie=req.cookie),
    "bilibili": lambda req: BilibiliCollector(),
    "youtube": lambda req: YouTubeCollector(api_key=req.api_key),
    "instagram": lambda req: InstagramCollector(),
    "tiktok": lambda req: TikTokCollector(),
}

@app.post("/api/v1/collect", response_model=APIResponse)
async def collect_data(
    request: CollectRequest,
    token: str = Depends(verify_token)
):
    """
    采集单条宣发数据
    """
    if request.platform not in COLLECTORS:
        return APIResponse(code=400, message=f"不支持的平台: {request.platform}")

    try:
        collector = COLLECTORS[request.platform](request)
        result = collector.collect(request.url)
        return APIResponse(code=0, message="success", data=result)
    except Exception as e:
        return APIResponse(
            code=500, 
            message=f"采集异常: {str(e)}",
            data=PromotionData(platform=request.platform, url=request.url, status="error", error_msg=str(e))
        )

@app.post("/api/v1/collect/batch", response_model=list[APIResponse])
async def collect_batch(
    requests: list[CollectRequest],
    token: str = Depends(verify_token)
):
    """
    批量采集宣发数据
    """
    results = []
    for req in requests:
        try:
            collector = COLLECTORS[req.platform](req)
            result = collector.collect(req.url)
            results.append(APIResponse(code=0, message="success", data=result))
        except Exception as e:
            results.append(APIResponse(
                code=500,
                message=str(e),
                data=PromotionData(platform=req.platform, url=req.url, status="error", error_msg=str(e))
            ))
        time.sleep(1)
    return results

@app.get("/api/v1/health")
async def health_check():
    """健康检查接口（用于保活）"""
    return {"status": "ok", "timestamp": time.time()}

@app.get("/api/v1/platforms")
async def list_platforms():
    """获取支持的平台列表"""
    return {
        "platforms": [
            {"id": "xiaohongshu", "name": "小红书", "requires_cookie": True},
            {"id": "douyin", "name": "抖音", "requires_cookie": True},
            {"id": "bilibili", "name": "B站", "requires_cookie": False},
            {"id": "youtube", "name": "YouTube", "requires_api_key": True},
            {"id": "instagram", "name": "Instagram", "requires_cookie": False},
            {"id": "tiktok", "name": "TikTok", "requires_cookie": False},
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
