#!/usr/bin/env python
#-*- coding: utf-8 -*-


import requests
import re


# spider, used to capture data from 12306
class spider(object):
    pass

class website(object):
    def __init__(self,url, username, password):
        self.url = url
        self.username = username
        self.password = password
    
    def login(self):
        pass

# train 
class train(object):
    def __init__(self, number, start, end):
        self.train_no = number
        self.start = start
        self.end = end
        

# city
class city(object):
    def __init__(self, code):
        self.code = code

# ticket
class ticket(object):
    def __init__(self, number, date, passenger, start, end):
        self.train_no = number
        self.date = date
        self.passenger = passenger
        self.start = start
        self.end = end

# passenger
class passenger(object):
    def __init__(self, name, ID):
        self.name = name
        self.ID = ID


if __name__ == '__main__':
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
    payload = {'leftTicketDTO.train_date': '2016-10-17', 'leftTicketDTO.from_station': 'ZBK', 'leftTicketDTO.to_station':'HGH', 'purpose_codes':'ADULT'}
    r = requests.get("https://kyfw.12306.cn/otn/leftTicket/init", params=payload, headers=header, verify=False)
    print(r.content)
    print(r.encoding)
    trains = re.findall(r'datatran="\w+"', r.content)
    print(trains)