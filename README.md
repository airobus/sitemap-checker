网站地图监控器 (Sitemap Checker)
一个强大且智能的自动化脚本，用于监控一个或多个网站的 sitemap 文件，并在发现新增网址时通过 PushPlus 发送实时通知。完全基于免费的 GitHub Actions 运行，无需您自己的服务器。

✨ 核心功能
多站点监控：通过简单的 domains.txt 配置文件，轻松管理需要监控的多个网站。

智能格式识别：自动识别并处理所有官方支持的 Sitemap 格式：

Sitemap 索引文件 (sitemap-index.xml)

标准 XML 文件 (sitemap.xml)

纯文本文件 (sitemap.txt)

实时推送通知：利用 PushPlus（微信推送），在发现新网址时第一时间通知您。

智能通知摘要：当新增网址过多时，自动生成摘要信息并附上完整的 GitHub 文件链接，避免通知内容过长导致发送失败。

完全自动化：基于 GitHub Actions，可按设定的时间表（默认为北京时间每天午夜）自动运行。

支持手动触发：可以随时在 GitHub Actions 页面手动触发检查，并支持输入一个临时网址进行一次性监控。

持久化日志：所有发现的新增网址都会被记录在以域名命名的日志文件中，并自动提交回您的仓库，方便追溯。

⚙️ 工作流程
项目的工作流程被设计得非常高效和智能：

触发任务：由 GitHub Actions 根据预设时间表或用户手动操作来触发。

读取配置：

如果用户手动输入了URL，则优先处理该URL。

否则，脚本会读取 domains.txt 文件，获取需要监控的所有 Sitemap 网址列表。

并发处理：脚本会开启一个线程池，同时对多个网址发起检查，大大提高了处理效率。

智能解析：对每个获取到的 Sitemap，脚本会自动判断其格式（索引、XML或纯文本）并正确解析出所有网址。

差异对比：将解析出的当前网址列表与保存在本地的历史记录文件（例如 example-com-urls.txt）进行对比，找出新增的网址。

执行操作：

无新网址：打印日志，任务结束。

有新网址：

更新历史记录文件。

将新增的网址追加到日志文件 (example-com-new_urls.txt) 中。

调用 PushPlus API 发送通知。

将所有被修改的文件自动 commit 和 push 回您的 GitHub 仓库。

🚀 快速开始
您只需要简单的几个步骤，就可以部署您自己的网站地图监控器。

1. Fork 本项目
点击本项目页面右上角的 Fork 按钮，将此项目复制到您自己的 GitHub 账户下。

2. 创建 domains.txt 文件
在您的项目根目录下，创建一个名为 domains.txt 的文件。在这个文件中，每行输入一个您想要监控的 sitemap 网址。您也可以使用 # 添加注释。

domains.txt 示例:

# Poki 游戏网站 (标准XML)
https://poki.com/sitemap

# CrazyGames 游戏网站 (Sitemap索引)
https://www.crazygames.com/sitemap-index.xml

# 某个博客 (纯文本)
https://example.com/sitemap.txt

3. 设置 PushPlus Token
为了能收到推送通知，您需要配置您的 PushPlus Token。

登录 PushPlus官网，获取您的 Token。

回到您 Fork 的 GitHub 仓库页面，点击 Settings -> Secrets and variables -> Actions。

点击绿色的 New repository secret 按钮。

在 Name 字段中，必须准确输入 PUSHPLUS_TOKEN。

在 Secret 字段中，粘贴您从 PushPlus 获取的 Token。

点击 Add secret 保存。

4. (可选) 修改通知中的仓库链接
默认情况下，当通知内容过多时，脚本会生成一个指向您仓库中日志文件的链接。这个链接是硬编码在 sitemap_checker.py 文件中的。

请打开 sitemap_checker.py，找到 send_push_notification_for_domain 函数，并修改以下两行：

# !!重要!! 请将下面的 'your-username/your-repo-name' 和 'main' 替换为您自己的仓库信息
repo_path = 'your-username/your-repo-name'  # 修改这里
branch = 'main'                             # 修改这里

🕹️ 如何使用
自动执行
项目默认配置为北京时间每天午夜 00:00 自动执行一次。您可以在 .github/workflows/sitemap_checker.yml 文件中修改 cron 表达式来更改执行时间。

手动执行
您可以随时手动触发检查：

进入您仓库的 Actions 选项卡。

在左侧选择 Sitemap Checker 工作流。

点击右侧的 Run workflow 下拉按钮。

[手动执行的截图]

检查所有网站：直接点击绿色的 Run workflow 按钮，脚本会读取 domains.txt 并检查所有网站。

检查单个网站：在 "要单独检查的Sitemap网址" 输入框中填入一个网址，然后点击 Run workflow 按钮。这对于临时测试非常有用。

📂 文件结构
.
├── .github/workflows/
│   └── sitemap_checker.yml   # GitHub Actions 配置文件，定义了自动化流程
├── domains.txt               # 您需要监控的Sitemap网址列表
├── sitemap_checker.py        # 项目的核心Python脚本
└── README.md                 # 就是您正在阅读的这个文件

🤝 贡献
欢迎任何形式的贡献！如果您有好的想法或发现了Bug，请随时提交 Pull Request 或创建 Issue。

📄 许可证
本项目采用 MIT License 授权。
