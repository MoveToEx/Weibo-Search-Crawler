from selenium import webdriver
from urllib import parse
import bs4

import html.parser

browser = webdriver.Chrome()

browser.minimize_window()

try:
    like_sum = 0
    comment_sum = 0
    share_sum = 0
    post_sum = 0

    text = parse.quote(input("Query text: "))

    browser.get(f'https://s.weibo.com/weibo?q={text}&nodup=1&page=1')

    browser.get(f'https://weibo.com/login.php')
    input("请在弹出窗口中登录您的账号，完成后请按回车")

    cookies = browser.get_cookies()

    for i in cookies:
        browser.add_cookie({
            'domain': "weibo.com",
            'name': i.get('name'),
            'value': i.get('value'),
            "expires": '',
            'path': '/',
            'httpOnly': False,
            'HostOnly': False,
            'Secure': False
        })

    browser.refresh()

    print('[INFO] Successfully imported cookies')

    max_page = 50
    print("开始爬取......")
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
            
            likes = int(likes) if likes.isdigit() else 0
            comments = int(comments) if comments.isdigit() else 0
            forwards = int(forwards) if forwards.isdigit() else 0

            like_sum += likes
            comment_sum += comments
            share_sum += forwards

        print(f"[INFO] Page {page} finished: post={post_sum}, like={like_sum}, comment={comment_sum}, share={share_sum}")

    print(f"转发数：{share_sum} 评论数：{comment_sum} 点赞数：{like_sum} 帖子数：{post_sum}")
finally:
    browser.close()
