import re
import requests
from typing import Optional
from models import PromotionData

class InstagramCollector:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }

    def extract_shortcode(self, url: str) -> Optional[str]:
        patterns = [
            r"/p/([a-zA-Z0-9_-]+)",
            r"/reel/([a-zA-Z0-9_-]+)",
            r"/tv/([a-zA-Z0-9_-]+)",
        ]
        for p in patterns:
            match = re.search(p, url)
            if match:
                return match.group(1)
        return None

    def collect(self, url: str) -> PromotionData:
        shortcode = self.extract_shortcode(url)
        if not shortcode:
            return PromotionData(
                platform="instagram", url=url, status="error",
                error_msg="无法提取shortcode"
            )

        try:
            embed_url = f"https://www.instagram.com/p/{shortcode}/embed/captioned"
            resp = requests.get(embed_url, headers=self.HEADERS, timeout=15)

            import json
            match = re.search(r"window\.__additionalDataLoaded\(['\"][^'\"]+['\"],\s*({.+?})\);", resp.text)
            if match:
                data = json.loads(match.group(1))
                media = data.get("graphql", {}).get("shortcode_media", {})

                return PromotionData(
                    platform="instagram",
                    url=url,
                    title=media.get("edge_media_to_caption", {}).get("edges", [{}])[0].get("node", {}).get("text", "")[:100],
                    author=media.get("owner", {}).get("username", ""),
                    likes=media.get("edge_media_preview_like", {}).get("count"),
                    comments=media.get("edge_media_to_parent_comment", {}).get("count"),
                    status="success"
                )

            return self._collect_from_meta(url, resp.text)

        except Exception as e:
            return PromotionData(
                platform="instagram", url=url, status="error",
                error_msg=str(e)
            )

    def _collect_from_meta(self, url: str, html: str) -> PromotionData:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            title = soup.find('meta', property='og:title')
            author = soup.find('meta', property='og:description')

            return PromotionData(
                platform="instagram",
                url=url,
                title=title.get('content', '')[:100] if title else None,
                author=author.get('content', '')[:50] if author else None,
                status="success",
                error_msg="仅获取到基础信息，互动数据需登录态"
            )
        except:
            return PromotionData(
                platform="instagram", url=url, status="error",
                error_msg="解析失败"
            )
