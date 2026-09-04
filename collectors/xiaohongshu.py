import re
import json
import requests
from typing import Optional
from models import PromotionData

class XiaoHongShuCollector:
    BASE_URL = "https://www.xiaohongshu.com"
    API_URL = "https://edith.xiaohongshu.com/api/sns/web/v1/feed"

    def __init__(self, cookie: Optional[str] = None):
        self.cookie = cookie
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://www.xiaohongshu.com",
            "Referer": "https://www.xiaohongshu.com/",
        }
        if cookie:
            self.headers["Cookie"] = cookie

    def extract_note_id(self, url: str) -> Optional[str]:
        patterns = [
            r"/explore/([a-zA-Z0-9]+)",
            r"/discovery/item/([a-zA-Z0-9]+)",
            r"noteId=([a-zA-Z0-9]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def collect(self, url: str) -> PromotionData:
        note_id = self.extract_note_id(url)
        if not note_id:
            return PromotionData(
                platform="xiaohongshu", url=url, status="error",
                error_msg="无法从URL提取笔记ID"
            )

        try:
            payload = {"source_note_id": note_id, "image_formats": ["jpg"]}
            response = requests.post(
                self.API_URL, 
                headers=self.headers,
                json=payload,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    note = data.get("data", {}).get("items", [{}])[0].get("note_card", {})
                    interact = note.get("interact_info", {})

                    return PromotionData(
                        platform="xiaohongshu",
                        url=url,
                        title=note.get("title", ""),
                        author=note.get("user", {}).get("nickname", ""),
                        publish_time=note.get("time"),
                        likes=self._parse_count(interact.get("liked_count")),
                        comments=self._parse_count(interact.get("comment_count")),
                        collects=self._parse_count(interact.get("collected_count")),
                        shares=self._parse_count(interact.get("share_count")),
                        status="success"
                    )

            return self._collect_from_html(url, note_id)

        except Exception as e:
            return PromotionData(
                platform="xiaohongshu", url=url, status="error",
                error_msg=str(e)
            )

    def _collect_from_html(self, url: str, note_id: str) -> PromotionData:
        try:
            resp = requests.get(url, headers=self.headers, timeout=15)
            match = re.search(r'<script>window\._SSR_HYDRATED_DATA=(.+?)</script>', resp.text)
            if match:
                data = json.loads(match.group(1))
                note = data.get("note", {}).get("noteDetailMap", {}).get(note_id, {})
                interact = note.get("interactInfo", {})

                return PromotionData(
                    platform="xiaohongshu",
                    url=url,
                    title=note.get("title", ""),
                    author=note.get("user", {}).get("nickname", ""),
                    likes=self._parse_count(interact.get("likedCount")),
                    comments=self._parse_count(interact.get("commentCount")),
                    collects=self._parse_count(interact.get("collectedCount")),
                    shares=self._parse_count(interact.get("shareCount")),
                    status="success"
                )
        except Exception as e:
            pass

        return PromotionData(
            platform="xiaohongshu", url=url, status="error",
            error_msg="HTML解析失败"
        )

    @staticmethod
    def _parse_count(value) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except:
            return None
