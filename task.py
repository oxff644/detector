import sqlite3

import urllib3
import yagmail
from celery import Celery, platforms
from requests_html import requests

from config import Config
from log import success, warning

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


platforms.C_FORCE_ROOT = True
celery_db = f"{Config.name}_worker.db"
sqlite3.connect(celery_db)
app_common = Celery(Config.name, broker=f"sqla+sqlite:///{celery_db}")


@app_common.task(shared=False)
def feishu(text: str, msg_type: str = "text", api_url: str = Config.feishu_API) -> None:

    requests.post(api_url, json={"msg_type": msg_type, "content": {"text": text}})


@app_common.task(shared=False)
def mail_to(
    content: str,
    subject: str = "",
    usr: str = Config.mail_usr,
    pwd: str = Config.mail_pwd,
    host: str = Config.mail_host,
    port: int = Config.mail_port,
    targets: list = None,
) -> None:
    targets = Config.mail_targets
    if not targets:
        targets = [usr]

    warning(
        f"收到邮件发送任务  发件人: [{usr}]  主机: [{host}:{port}]  目标: [{targets}]  内容: [{len(content)}]"
    )
    with yagmail.SMTP(
        user=usr,
        password=pwd,
        port=port,
        smtp_ssl=False,
        smtp_skip_login=False if pwd else True,
        soft_email_validation=False,
        host=host if host else "smtp." + usr.split("@")[-1],
    ) as client:

        client.send(to=targets, subject=subject, contents=content)
        success(
            f"成功发送  发件人: [{usr}]  主机: [{host}:{port}]  目标: [{targets}]  内容: [{len(content)}]"
        )
