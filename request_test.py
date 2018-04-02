# -*- coding: utf-8 -*-
import time
#import datetime
import json

import arrow
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

from helper_jj import JiaoJing
from helper_download import Downloader
from helper_kakou_v2 import Kakou


class JiaoTest(object):
    def __init__(self):
        self.ini = {
            'host': '44.89.27.135',
            'port': 8383,
	    'username': 'hcq',
	    'password': 'maci'
        }
        self.ini2 = {
            'host': '44.89.27.135',
            'port': 5003,
	    'username': 'hcq',
	    'password': 'maci'
        }
        self.jj = JiaoJing(**self.ini)
        self.kk = Kakou(**self.ini2)
        self.dl = Downloader()
    
    def test_kakou(self):
        """上传卡口数据"""
        #print(self.jj.get_kkdd(),)
        r = self.jj.get_kakou_by_id(55500014)
        print(r['hphm'].encode('utf-8'))
        #print(self.jj.get_kakou(55500014, 55500016))

    def test_get_img(self):
        """上传卡口数据"""
        r = self.jj.get_kakou(55500717, 55500916, per_page=200)
        #tt = time.time()
        #for i in r['items']:
        #    t = arrow.get(i['jgsj'])
        #    path = '/data/kakou/SpreadData/{0}/{1}'.format(t.format('YYYYMM/DD/HH'), i['kkbh'])
        #    self.dl.fetch_img(i['imgurl'], path, i['id'])
        #print(self.jj.get_kakou(55500014, 55500016))
        #print(time.time() - tt)

    def test_post_kakou(self, start_id, end_id):
        r = self.jj.get_kakou(start_id, end_id, per_page=200)
        items = []
        for i in r['items']:
            try:
                if i['kkbh'] != '5334':
                    continue
                if i['hphm'] == '车牌':
                    i['hphm'] = '-'
                t = arrow.get(i['jgsj'])
                i['tjtp'] = '{0}/{1}/{2}.jpg'.format(t.format('YYYYMM/DD/HH'), i['kkbh'], i['id'])
                path = '/data/kakou/SpreadData/{0}/{1}'.format(t.format('YYYYMM/DD/HH'), i['kkbh'])
                self.dl.fetch_img(i['imgurl'], path, i['id'])
                items.append(i)
            except Exception as e:
                print(e)
        if len(items) > 0:
            self.kk.post_kakou(items)

    def test_upload_data(self):
        id_flag = 55500817
        step = 20
        for i in range(100):
            self.test_post_kakou(id_flag+1, id_flag+step)
            id_flag += step


if __name__ == '__main__':  # pragma nocover
    kt = JiaoTest()
    kt.test_get_img()

