#!/usr/bin/env python
#-*- coding: utf-8 -*-


import requests
import re
import json

# disable warning
from requests.packages.urllib3.exceptions import InsecureRequestWarning,InsecurePlatformWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

class train(object):
    __init__(self,number='',from_station='',to_station='',
             date='', begin='',end='',pass_station=''):
        self.number=number;
        self.from_station=from_station;
        self.to_station=to_station;
        self.date=date;
        self.begin=begin;
        self.end=end;
        self.pass_station=pass_station;
        
    





if __name__ == '__main__':
    
    # 获取网页数据
    header = {
        "Host": "kyfw.12306.cn",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
        "If-Modified-Since": "0",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
        "Referer": "https://kyfw.12306.cn/otn/leftTicket/init",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "en-us;q=0.5,en;q=0.3"
    }
    url = "https://kyfw.12306.cn/otn/leftTicket/queryC" + "?" + "leftTicketDTO.train_date=" + "2016-10-22" + "&leftTicketDTO.from_station=" + "ZBK" + "&leftTicketDTO.to_station=" + "HGH" + "&purpose_codes=" + "ADULT"
    r = requests.get(url, headers=header, verify=False)
    train = r.json();
    
    #分析抓取的数据
    #print(type(train))
    #print json.dumps(train, indent=4)
    print("所有车次")
    for train_data in train['data']:
        print(train_data['queryLeftNewDTO']['station_train_code'])
 
    
   