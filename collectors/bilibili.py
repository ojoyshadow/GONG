import re
import requests
from typing import Optional
from models import PromotionData

class BilibiliCollector:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.bilibili.com/",
    }

    def extract_bvid(self, url: str) -> Optional[str]:
        patterns = [
            r"/video/(BV\w+)",
            r"/video/(av\d+)",
        ]
        for p in patterns:
            match = re.search(p, url)
            if match:
                return match.group(1)
        return None

    def collect(self, url: str) -> PromotionData:
        bvid = self.extract_bvid(url)
        if not bvid:
            return PromotionData(
                platform="bilibili", url=url, status="error",
                error_msg="无法提取BV号"
            )

        try:
            info_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
            resp = requests.get(info_url, headers=self.HEADERS, timeout=15)
            data = resp.json()

            if data.get("code") == 0:
                video = data.get("data", {})
                stat = video.get("stat", {})
                owner = video.get("owner", {})

                return PromotionData(
                    platform="bilibili",
                    url=url,
                    title=video.get("title", ""),
                    author=owner.get("name", ""),
                    publish_time=video.get("pubdate"),
                    views=stat.get("view"),
                    likes=stat.get("like"),
                    comments=stat.get("reply"),
                    collects=stat.get("favorite"),
                    shares=stat.get("share"),
                    status="success"
                )

            return PromotionData(
                platform="bilibili", url=url, status="error",
                error_msg=f"B站API错误: {data.get('message')}"
            )

        except Exception as e:
            return PromotionData(
                platform="bilibili", url=url, status="error",
                error_msg=str(e)
            )
