import datetime
import json
import logging
import sys
from dataclasses import dataclass, field
from urllib.parse import urljoin

import urllib3
import yagmail
from celery import Celery
from requests_html import HTMLSession
from tqdm import tqdm

import config
from common import DB
from log import info, success, warning
from task import feishu, mail_to

DEBUG = len(sys.argv) == 2 and sys.argv[1] == "debug"


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


if sys.version_info[0] == 2:
    sys.version_info.major
    sys.setdefaultencoding("utf-8")

# now_time = datetime.datetime.today().strftime('Y%.m%.%d')


@dataclass
class Detector:
    report_url: str = "https://m.aliyun.com/doc/notice_list/9213612.html"
    # email_from = '信息安全管理部<xxx@xxx.com>'
    # mail_tmplate = '<br>安全漏洞预警</br><a href={url}><br>{title}</br>{body}'

    def __post_init__(self):
        """
        初始化Session
        """
        self.session = HTMLSession()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Mobile Safari/537.36"
        }
        self.session.verify = False
        self.tb = DB()

    def get_data(self):
        """
        获得基础数据
        """
        resp = self.session.get(self.report_url)
        for tag_a in tqdm(list(resp.html.pq("div.xs-content > a").items())):
            url = urljoin(resp.url, tag_a.attr("href"))
            tag_date, tag_title = tag_a("div")
            self.save_data(
                {
                    "date": tag_date.text,
                    "title": tag_title.text,
                    "url": url,
                    "content": self.get_content(url),
                }
            )

    def get_content(self, url):
        """
        获得详情
        """
        resp = self.session.get(url)
        datas = {}
        last_key = None
        for tag_p in resp.html.pq("div#se-knowledge > p").items():
            key = tag_p("strong").text()
            text = tag_p.text().strip()
            if key:
                last_key = key
            elif text and last_key:
                if last_key not in datas:
                    datas[last_key] = ""
                datas[last_key] += f"{text}\n"
            elif not text:
                last_key = None
        return datas

    def save_data(self, data):
        """
        存储数据并判断是否已存在
        """
        if self.tb.add(data) or DEBUG:
            self.notice(data)

    def notice(self, data):
        """
        发起预警
        """
        if datetime.datetime.today().strftime("%m-%d") != data["date"] and not DEBUG:
            return
        title, body = self.format_msg(data)
        success(f"notice {title}")
        feishu.delay(f"{title}\n\n{body}")
        mail_to.delay(body, title)
        # mail_to(body, title)

    def format_msg(self, data):
        """
        整理数据成消息
        """
        # body = "body"
        title = f'{data["title"]}\n'

        body = f"漏洞等级: {data['content'].get('漏洞评级','未知').strip().split()[-1]}\n参考链接: <a href='{data['url']}' target='_blank'></a> {data['url']}"

        return title, body


if __name__ == "__main__":
    Detector().get_data()
