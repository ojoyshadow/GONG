import re
import os
from typing import Optional
from models import PromotionData

class YouTubeCollector:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if self.api_key:
            try:
                from googleapiclient.discovery import build
                self.youtube = build("youtube", "v3", developerKey=self.api_key)
            except ImportError:
                self.youtube = None
        else:
            self.youtube = None

    def extract_video_id(self, url: str) -> Optional[str]:
        patterns = [
            r"v=([a-zA-Z0-9_-]{11})",
            r"youtu\.be/([a-zA-Z0-9_-]{11})",
            r"embed/([a-zA-Z0-9_-]{11})",
        ]
        for p in patterns:
            match = re.search(p, url)
            if match:
                return match.group(1)
        return None

    def collect(self, url: str) -> PromotionData:
        if not self.youtube:
            return PromotionData(
                platform="youtube", url=url, status="error",
                error_msg="未配置YouTube API Key"
            )

        video_id = self.extract_video_id(url)
        if not video_id:
            return PromotionData(
                platform="youtube", url=url, status="error",
                error_msg="无法提取视频ID"
            )

        try:
            response = self.youtube.videos().list(
                part="snippet,statistics",
                id=video_id
            ).execute()

            if not response.get("items"):
                return PromotionData(
                    platform="youtube", url=url, status="error",
                    error_msg="视频不存在或不可见"
                )

            item = response["items"][0]
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})

            return PromotionData(
                platform="youtube",
                url=url,
                title=snippet.get("title", ""),
                author=snippet.get("channelTitle", ""),
                publish_time=snippet.get("publishedAt"),
                views=self._parse_int(stats.get("viewCount")),
                likes=self._parse_int(stats.get("likeCount")),
                comments=self._parse_int(stats.get("commentCount")),
                shares=None,
                status="success"
            )

        except Exception as e:
            return PromotionData(
                platform="youtube", url=url, status="error",
                error_msg=str(e)
            )

    @staticmethod
    def _parse_int(value) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except:
            return None
