import re
import requests
from typing import Optional
from models import PromotionData

class TikTokCollector:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://www.tiktok.com/",
    }

    def extract_video_id(self, url: str) -> Optional[str]:
        patterns = [
            r"/video/(\d+)",
            r"/v/(\d+)",
        ]
        for p in patterns:
            match = re.search(p, url)
            if match:
                return match.group(1)
        return None

    def collect(self, url: str) -> PromotionData:
        video_id = self.extract_video_id(url)
        if not video_id:
            return PromotionData(
                platform="tiktok", url=url, status="error",
                error_msg="无法提取视频ID"
            )

        try:
            oembed_url = f"https://www.tiktok.com/oembed?url={url}"
            resp = requests.get(oembed_url, headers=self.HEADERS, timeout=15)
            data = resp.json()

            if "title" in data:
                return PromotionData(
                    platform="tiktok",
                    url=url,
                    title=data.get("title", ""),
                    author=data.get("author_name", ""),
                    status="success",
                    error_msg="TikTok公开API仅提供基础信息，详细数据需官方API或商业服务"
                )

            return PromotionData(
                platform="tiktok", url=url, status="error",
                error_msg="无法获取数据"
            )

        except Exception as e:
            return PromotionData(
                platform="tiktok", url=url, status="error",
                error_msg=str(e)
            )
