import requests
from bs4 import BeautifulSoup
import time
import os
import json
from urllib.parse import urlparse
import concurrent.futures

# --- 辅助函数 ---

def get_filename_prefix_from_url(url):
    """根据URL生成一个安全的文件名前缀, e.g., 'https://a.b.com/sitemap' -> 'a-b-com'"""
    try:
        netloc = urlparse(url).netloc
        # 替换点为横线，移除常见的子域名如 www
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        return netloc.replace('.', '-')
    except Exception:
        # 如果URL格式不正确，则返回一个基于时间戳的通用名称
        return f"invalid-url-{int(time.time())}"

# --- 新增的核心处理函数 ---

def send_push_notification_for_domain(new_urls, domain_prefix):
    """为特定域名发送推送消息"""
    token = os.environ.get('PUSHPLUS_TOKEN')
    if not token:
        return

    url = "https://www.pushplus.plus/send"
    headers = {"Content-Type": "application/json"}
    
    title = f"[{domain_prefix}] 发现新 Sitemap URL"
    content_urls = "\n".join(sorted(list(new_urls)))
    
    data = {
      "token": token,
      "title": title,
      "content": f"检测到 {len(new_urls)} 个新增 URL:\n{content_urls}"
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        print(f"[{domain_prefix}] 推送消息发送成功。")
    except requests.exceptions.RequestException as e:
        print(f"[{domain_prefix}] 推送消息发送失败: {e}")


def process_sitemap(sitemap_url):
    """处理单个sitemap URL的完整逻辑"""
    if not sitemap_url or not sitemap_url.startswith('http'):
        print(f"[警告] 无效或空的 URL: '{sitemap_url}'，跳过处理。")
        return
        
    domain_prefix = get_filename_prefix_from_url(sitemap_url)
    print(f"--- 开始处理: {sitemap_url} (文件前缀: {domain_prefix}) ---")
    
    url_file = f"{domain_prefix}-urls.txt"
    new_urls_file = f"{domain_prefix}-new_urls.txt"

    try:
        response = requests.get(sitemap_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml-xml')
        current_urls = {url.loc.text for url in soup.find_all('url')}

        if not current_urls:
            print(f"[{domain_prefix}] 未在此 sitemap 中找到任何 URL。")
            return

        existing_urls = set()
        if os.path.exists(url_file):
            with open(url_file, 'r', encoding='utf-8') as f:
                existing_urls = {line.strip() for line in f if line.strip()}

        new_urls = current_urls - existing_urls
        print(f"[{domain_prefix}] 已获取 {len(current_urls)} 个 URL，发现 {len(new_urls)} 个新增 URL。")

        if new_urls:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            with open(url_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(sorted(list(current_urls))))
            
            with open(new_urls_file, 'a', encoding='utf-8') as f:
                f.write('------------------------\n')
                f.write(f"检查时间: {timestamp}\n")
                f.write("\n".join(sorted(list(new_urls))))
                f.write('\n\n')
            
            print(f"[{domain_prefix}] 已将新增 URL 记录到 {new_urls_file}")
            send_push_notification_for_domain(new_urls, domain_prefix)
        
    except requests.exceptions.RequestException as e:
        print(f"[错误] 处理 {sitemap_url} 失败: {e}")
    except Exception as e:
        print(f"[未知错误] 处理 {sitemap_url} 时发生意外: {e}")
    finally:
        print(f"--- 完成处理: {sitemap_url} ---\n")


# --- 原有函数 (保留，不做改动) ---

def fetch_sitemap(sitemap_url):
    """(旧函数，保留) 获取 sitemap 并提取新增的 URL"""
    SITEMAP_URL = sitemap_url
    URL_FILE = 'urls.txt'
    NEW_URLS_FILE = 'new_urls.txt'
    # ... 原有逻辑 ...

def send_push_notification(new_urls):
    """(旧函数，保留) 发送推送消息到 pushplus"""
    # ... 原有逻辑 ...


# --- 主程序入口 ---

if __name__ == "__main__":
    # 检查是否通过手动触发的输入提供了单个URL
    manual_url = os.environ.get('MANUAL_SITEMAP_URL')

    if manual_url:
        print(f"检测到手动输入的URL，将只处理: {manual_url}")
        process_sitemap(manual_url)
        print("手动任务处理完毕。")
    else:
        # 如果没有手动输入，则执行原有的批量处理逻辑
        DOMAINS_FILE = 'domains.txt'
        MAX_WORKERS = 10  # 最多同时处理5个网站

        if not os.path.exists(DOMAINS_FILE):
            print(f"错误: 找不到配置文件 '{DOMAINS_FILE}'。")
            with open(DOMAINS_FILE, 'w', encoding='utf-8') as f:
                f.write("# 请在此处输入sitemap网址，每行一个\n")
                f.write("https://play.dictionary.com/sitemap.xml\n")
            print("已为您创建一个示例文件，请修改后重新运行。")
        else:
            with open(DOMAINS_FILE, 'r', encoding='utf-8') as f:
                urls_to_process = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

            if not urls_to_process:
                print("domains.txt 文件中没有有效的网址可供处理。")
            else:
                print(f"发现 {len(urls_to_process)} 个网址，开始并发处理...")
                with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    executor.map(process_sitemap, urls_to_process)
                print("所有任务处理完毕。")
