from selenium import webdriver
from urllib import parse
import bs4
import json
import html.parser
import re

browser = webdriver.Chrome()
browser.minimize_window()
browser.get('https://weibo.com')

cookies = []

def parse_int(s: str) -> int:
    s = s.strip()
    if m := re.match(r'(\d+)万\+?', s):
        return int(m.group(1)) * 10000
    elif s.isdigit():
        return int(s)
    else:
        return 0

try:
    with open('cookies.json', 'r', encoding='utf8') as f:
        cookies = json.loads(f.read())
        for i in cookies:
            browser.add_cookie(i)
except FileNotFoundError:
    open('cookies.json', 'x')

like_sum = 0
comment_sum = 0
share_sum = 0
post_sum = 0

text = parse.quote(input("Query text: "))

browser.get(f'https://s.weibo.com/weibo?q={text}&nodup=1&page=1')

if not cookies:
    browser.get(f'https://weibo.com/login.php')
    input("请在弹出窗口中登录您的账号，完成后请按回车")

    cookies = [
        {
            'domain': "weibo.com",
            'name': i.get('name'),
            'value': i.get('value'),
            "expires": '',
            'path': '/',
            'httpOnly': False,
            'HostOnly': False,
            'Secure': False
        } for i in browser.get_cookies()
    ]

    for i in cookies:
        browser.add_cookie(i)

    with open('cookies.json', 'w', encoding='utf8') as f:
        f.write(json.dumps(cookies, ensure_ascii=False))

browser.refresh()

print('[INFO] Successfully imported cookies')

max_page = 50

print("[INFO] Starting crawler...")
for page in range(1, max_page+1):
    browser.get(f'https://s.weibo.com/weibo?q={text}&nodup=1&page={page}')

    if browser.page_source.find('抱歉，未找到相关结果。') != -1:
        continue

    html = bs4.BeautifulSoup(browser.page_source, 'html.parser')

    items = [x.select_one('.card-act') for x in html.select(
        'div[action-type="feed_list_item"]') if not x.select('.card-comment')]
    
    post_sum += len(items)
    
    for i in items:
        likes = i.select_one('.woo-like-count').text.strip()
        comments = i.select_one('a[action-type="feed_list_comment"]').text.strip()
        forwards = i.select_one('a[action-type="feed_list_forward"]').text.strip()
        
        likes = parse_int(likes)
        comments = parse_int(comments)
        forwards = parse_int(forwards)

        like_sum += likes
        comment_sum += comments
        share_sum += forwards

    print(f"[INFO] Page {page} finished: post={post_sum}, like={like_sum}, comment={comment_sum}, share={share_sum}")

browser.close()
print("[INFO] Crawler stopped")

print(f"帖子数：{post_sum}")
print(f"点赞数：{like_sum}")
print(f"评论数：{comment_sum}")
print(f"转发数：{share_sum}")

