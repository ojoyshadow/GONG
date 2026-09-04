# PopMart 宣发数据采集服务

支持小红书、抖音、B站、YouTube、Instagram、TikTok 的宣发数据自动化采集。

## 快速部署到 Render

1. Fork 或上传本仓库到 GitHub
2. 打开 [render.com](https://render.com) → New Web Service
3. 连接 GitHub 仓库
4. 确认配置：
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port 10000`
5. 添加环境变量 `API_KEY`（自己编一个复杂密码）
6. 点击 Deploy

## API 使用

### 采集单条数据
```bash
POST /api/v1/collect
Authorization: Bearer your-api-key
Content-Type: application/json

{
  "platform": "bilibili",
  "url": "https://www.bilibili.com/video/BV1GJ411x7h7"
}
```

### 支持的平台
- `xiaohongshu` - 小红书（需要 Cookie）
- `douyin` - 抖音（需要 Cookie）
- `bilibili` - B站（无需认证）
- `youtube` - YouTube（需要 API Key）
- `instagram` - Instagram（无需认证，数据有限）
- `tiktok` - TikTok（无需认证，数据有限）

## 环境变量

| 变量 | 说明 | 必填 |
|------|------|------|
| API_KEY | API 鉴权密钥 | 是 |
| YOUTUBE_API_KEY | YouTube Data API 密钥 | 采集 YouTube 时需要 |
