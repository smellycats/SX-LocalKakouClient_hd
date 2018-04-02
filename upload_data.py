# -*- coding: utf-8 -*-
import time
import json
import socket
import base64

import arrow

import helper
from helper_kakou_v2 import Kakou
from helper_consul import ConsulAPI
from my_logger import *
from my_yaml import MyYAML


debug_logging('/home/logs/error.log')
logger = logging.getLogger('root')


class UploadData(object):
    def __init__(self):
        # 配置文件
        self.ini = MyYAML('/home/my.yaml')
        self.my_ini = self.ini.get_ini()
        self.flag_ini = MyYAML('/home/flag.yaml')
        # request方法类
        self.hd = Kakou(**dict(self.my_ini['hd']))
        self.ys = Kakou(**dict(self.my_ini['ys']))
        self.con = ConsulAPI()
        
        self.hd.status = True
        self.ys.status = True

        self.step = self.my_ini['step']

        self.uuid = None                    # session id
        self.session_time = time.time()     # session生成时间戳
        self.ttl = dict(self.my_ini['consul'])['ttl']               # 生存周期
        self.lock_name = dict(self.my_ini['consul'])['lock_name']   # 锁名

        self.local_ip = '10.47.223.148'#socket.gethostbyname(socket.gethostname())  # 本地IP
        self.maxid = 0

        self.id_flag = self.flag_ini.get_ini()['id']

    def get_id2(self):
        """获取上传id"""
        r = self.con.get_id()[0]
        return json.loads(base64.b64decode(r['Value']).decode()), r['ModifyIndex']

    def get_id(self):
        """获取上传id"""
        return self.id_flag

    def set_id2(self, _id, modify_index):
        """设置ID"""
        if self.con.put_id(_id, modify_index):
            print(_id)

    def set_id(self, _id, msg=''):
        """设置ID"""
        self.id_flag = _id
        self.flag_ini.set_ini({'id': _id})
        print(self.id_flag)
        logger.info('{0} {1}'.format(_id, msg))

    def get_lost(self):
        """获取未上传数据id列表"""
        r = self.con.get_lost()[0]
        return json.loads(base64.b64decode(r['Value']).decode()), r['ModifyIndex']

    def get_lock(self):
        """获取锁"""
        if self.uuid is None:
            self.uuid = self.con.put_session(self.ttl, self.lock_name)['ID']
            self.session_time = time.time()
        p = False
        # 大于一定时间间隔则更新session
        # t = time.time() - self.session_time
        if (time.time() - self.session_time) > (self.ttl - 10):
            self.con.renew_session(self.uuid)
            self.session_time = time.time()
            p = True
        l = self.con.get_lock(self.uuid, self.local_ip)
        if p:
            print(self.uuid, l)
        # session过期
        if l == None:
            self.uuid = None
            return False
        return l

    def post_info(self):
        """上传数据"""
        #id, modify_index = self.get_id()
        id = self.get_id()
        if self.maxid == 0 or self.maxid <= id:
            self.maxid = self.ys.get_maxid()
            return 0
        if self.maxid <= (id+self.step):
            last_id = self.maxid
        else:
            last_id = id + self.step
        info = self.ys.get_kakou(id+1, last_id, 1, self.step+1)
        #print('maxid=%s'%self.maxid)
        #print('total_count=%s'%info['total_count'])
        # 如果查询数据为0
        if info['total_count'] == 0:
            self.set_id(last_id, modify_index)
            return 0
        
        items = []
        for i in info['items']:
            i['tjtp'] = helper.created_url(i['imgurl'])
            items.append(i)
        if len(items) > 0:
            self.hd.post_kakou(items)
        # 设置最新ID
        #self.set_id(last_id, modify_index)
        self.set_id(last_id)
        return info['total_count']


    def main_loop(self):
        while 1:
            try:
                #if not self.get_lock():
                #    time.sleep(2)
                #    continue
                n = self.post_info()
                if n < self.step:
                    time.sleep(0.5)
            except Exception as e:
                logger.exception(e)
                time.sleep(15)


