# B站UP主动态钉钉机器人

这是一个自动爬取B站UP主动态，并发送到钉钉的机器人。

## 功能特性

- 🤖 定时检查B站UP主的最新动态
- 📢 自动发送到钉钉机器人
- 💾 记录已发送动态，避免重复推送
- 🎬 支持视频和文字动态

## 快速开始

### 1. 环境要求

- Python 3.8+
- pip

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置

#### 获取钉钉Webhook

1. 打开钉钉群
2. 点击群设置 → 智能群助手
3. 添加自定义机器人
4. 复制 Webhook 地址到 `.env` 文件

#### 配置环境变量

编辑 `.env` 文件：

```
DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN
DINGTALK_SECRET=（可选）
CHECK_INTERVAL=5
```

### 4. 运行

```bash
python bot.py
```

## 项目结构

```
.
├── bot.py                 # 主程序
├── config.py              # 配置文件
├── bilibili_spider.py     # B站爬虫
├── dingtalk_sender.py     # 钉钉发送器
├── requirements.txt       # 依赖列表
├── .env                   # 环境变量
├── data/                  # 数据目录
└── README.md              # 说明文档
```

## 部署

### Docker部署

```bash
docker build -t bili-dingtalk-bot .
docker run -d --name bili-bot --env-file .env bili-dingtalk-bot
```

### 云服务器部署

推荐使用 PM2 管理进程：

```bash
npm install -g pm2
pm2 start bot.py --name bili-dingtalk-bot
pm2 save
```

## 常见问题

### 消息不发送怎么办？

1. 检查 `.env` 文件中的 Webhook URL 是否正确
2. 查看日志输出是否有错误信息
3. 确保网络连接正常

### 如何修改检查频率？

编辑 `.env` 文件中的 `CHECK_INTERVAL` 参数（单位：分钟）

## License

MIT