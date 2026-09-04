import re
import requests
from typing import Optional
from models import PromotionData

class DouyinXingtuCollector:
    def __init__(self, cookie: Optional[str] = None):
        self.cookie = cookie
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://www.douyin.com/",
        }
        if cookie:
            self.headers["Cookie"] = cookie

    def extract_video_id(self, url: str) -> Optional[str]:
        patterns = [
            r"/video/(\d+)",
            r"modal_id=(\d+)",
            r"/share/video/(\d+)",
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
                platform="douyin", url=url, status="error",
                error_msg="无法提取视频ID"
            )

        try:
            api_url = f"https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={video_id}"
            resp = requests.get(api_url, headers=self.headers, timeout=15)
            data = resp.json()

            if data.get("status_code") == 0:
                aweme = data.get("aweme_detail", {})
                stats = aweme.get("statistics", {})
                author = aweme.get("author", {})

                return PromotionData(
                    platform="douyin",
                    url=url,
                    title=aweme.get("desc", "")[:100],
                    author=author.get("nickname", ""),
                    publish_time=aweme.get("create_time"),
                    views=stats.get("play_count"),
                    likes=stats.get("digg_count"),
                    comments=stats.get("comment_count"),
                    shares=stats.get("share_count"),
                    collects=stats.get("collect_count"),
                    status="success"
                )

            return PromotionData(
                platform="douyin", url=url, status="error",
                error_msg="API返回异常"
            )

        except Exception as e:
            return PromotionData(
                platform="douyin", url=url, status="error",
                error_msg=str(e)
            )
