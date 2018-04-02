# -*- coding: utf-8 -*-
import shutil
from urllib import parse

#import requests

PATH_DICT = {
    '44.89.51.3:8088': 'hyjj',
    '44.89.51.4:8088': 'hyjj2'
}

def get_url_img(url, path, s):
    """根据URL地址抓图到本地文件"""
    r = s.get(url, stream=True, timeout=5)

    if r.status_code == 200:
        with open(path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    # 非200响应,抛出异常
    r.raise_for_status()


def created_url(url):
    o = parse.urlparse(url)
    path = '{0}{1}'.format(PATH_DICT.get(o.netloc, ''), o.path)
    return path
