#!/usr/bin/env python
#-*- coding: utf-8 -*-


import requests
import re
import json
import sys
import random
import urllib

# disable warning
from requests.packages.urllib3.exceptions import InsecureRequestWarning,InsecurePlatformWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

# Set default encoding to utf-8

MAX_TRIES = 10

common_headers = {
    "Host": "kyfw.12306.cn",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
    "Accept": "*/*",
    "x-Requested-With": "XMLHttpRequest",
    "If-Modified-Since": "0",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, sdch, br",
    "Accept-Language": "zh-CN,zh;q=0.8"

}

specific_headers={
    'queryByTrainNo':{
        'Referer': 'https://kyfw.12306.cn/otn/queryTrainInfo/init',
        'method':'GET'
    },
    'query_trainlist':{
        'Referer': 'https://kyfw.12306.cn/otn/queryTrainInfo/init',
        'method':'GET'
    },
    'get_pass_code':{
        'Referer': 'https://kyfw.12306.cn/otn/queryTrainInfo/init',
        'method':'GET'
    },
    'checkRandCodeAnsyn':{
        'Referer': 'https://kyfw.12306.cn/otn/queryTrainInfo/init',
        'method':'POST',
        'Cache-Control': 'no-cache',
        'x-requested-with': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://kyfw.12306.cn'
        
    }    
}

urls={
    'queryByTrainNo':'https://kyfw.12306.cn/otn/queryTrainInfo/query?',
    'query_trainlist':'https://kyfw.12306.cn/otn/resources/js/query/train_list.js?scriptVersion=1.0',
    'get_pass_code':'https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?',
    'checkRandCodeAnsyn':'https://kyfw.12306.cn/otn/passcodeNew/checkRandCodeAnsyn'
}

def session_header_update(old_header, new_headers):
    keys = [
        'Referer',
        'Cache-Control',
        'x-requested-with',
        'Content-Type',
        'Origin'
    ]
    for key in keys:
        if key in new_headers:
            old_header[key]=new_headers[key]; 

# 列车
class train(object):
    def __init__(self, train_no='', train_code='', date=''):
        self.train_no=train_no;
        self.train_code=train_code;
        self.date=date;
        if train_no == '' and train_code != '':
            self.train_no = self.train_code2no(train_code);
        self.session=requests.Session();
            
    def __search_train_no_by_code(self, train_code, train_list):
        key1 = sorted(train_list.keys(),reverse=True)[0];
        print(key1)
        for key2 in train_list[key1].keys():
            for one_train in train_list[key1][key2]:
                train_code_in_list = one_train['station_train_code'].upper();
                if train_code_in_list.find(train_code.upper()+'(') != -1:
                    train_no = train_code_in_list = one_train['train_no']
                    return train_no;
                    
    def train_code2no(self, train_code=''):
        if train_code == '':
            train_code = self.train_code;
        if train_code == '':
            print("Please input correct train code")
            return None;
        
        s = self.session;
        my_header = common_headers;
        session_header_update(my_header, specific_headers['query_trainlist']);
        req=requests.Request(specific_headers['query_trainlist']['method'], urls['query_trainlist'], headers=my_header);
        prepped=s.prepare_request(req);
        
        i = 0
        while i < MAX_TRIES:
            resp=s.send(prepped, verify=False);
            # resp.content is var train_list = {}
            #print(resp.content)
            str=resp.text;
            if str.find(u'train_list =') != -1:
                print(u'查询成功');
                str_list = str.split('=')
                train_list=json.loads(str_list[1]);

                for key in train_list:
                    #print(key)
                    pass
                break;
            else:
                i = i + 1;
                print(u'查询失败,重试第%d次' %i);
        if i == 11:
            print(u'查询失败');
            return None;
        
        # 查询成功，开始解析数据， train_list包含所有的信息
        train_no = self.__search_train_no_by_code(train_code, train_list);
        print(u'%s对应的NO是%s' %(train_code, train_no));
        return train_no;
        
    def __get_pass_code(self, module='other'):
        d = {'other':{'rand':'sjrand'}}
        if not module in d:
            print(u'无效的 module: %s' % (module))
            return None;
        
        s = self.session;
        my_header = common_headers;
        session_header_update(my_header, specific_headers['get_pass_code']);
        
        url = '%smodule=%s&rand=%s&' % (urls['get_pass_code'], module, d[module]['rand']);
        req=requests.Request(specific_headers['get_pass_code']['method'], url, headers=my_header);
        prepped=s.prepare_request(req);
        i = 0;
        while i < MAX_TRIES:
            resp=s.send(prepped, verify=False, stream=True);
            cookies=requests.utils.dict_from_cookiejar(s.cookies);

            with open('captcha.bmp', 'wb') as fd:
                for chunk in resp.iter_content():
                    fd.write(chunk)    
            print(u'请输入4位图片验证码(回车刷新验证码):')
            passcode = raw_input() 
        
            my_header = common_headers;
            session_header_update(my_header, specific_headers['checkRandCodeAnsyn']);
            payload={'rand':d[module]['rand'], 'randCode':passcode};
            payload=urllib.urlencode(payload);
            url = '%s' % (urls['checkRandCodeAnsyn']);
            req=requests.Request(specific_headers['checkRandCodeAnsyn']['method'], url, cookies=cookies, headers=my_header, data=payload);
            prepped=s.prepare_request(req); 
            resp=s.send(prepped, verify=False);
        
            # {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":{"result":"1","msg":"randCodeRight"},"messages":[],"validateMessages":{}}
            obj = resp.json();
            if (obj['data']['result'] == '1'):
                print(u'校验验证码成功')
                str=resp.content; 
            
                return passcode
            else:
                print(u'校验验证码失败');
                i = i + 1;
                continue  

        return None;
    
    def query_by_train_no(self,train_no='',date=''):
        if train_no == '':
            train_no = self.train_no;
        
        if train_no == '':
            print("Please input correct train_no");
            return None;
        
        if date == '':
            date = self.date;
        
        if date == '':
            print(u"请输入日期");
            return None;
        
        pass_code = self.__get_pass_code(module='other');
        
        # we get correct train_no now, start query
        s = self.session;
        my_header = common_headers;
        session_header_update(my_header, specific_headers['queryByTrainNo']);
        url = '%sleftTicketDTO.train_no=%s&leftTicketDTO.train_date=%s&rand_code=%s' %(urls['queryByTrainNo'],train_no,date,pass_code);
        req=requests.Request(specific_headers['queryByTrainNo']['method'], url, headers=my_header);
        prepped=s.prepare_request(req);
        resp=s.send(prepped, verify=False);
        
        # resp.content is var train_list = {}
        #print(resp.content)
        str=resp.text; 
        print(str);

#乘客
class passenger(object):
    pass

#订单
class order(object):
    pass

def main():
    one_train=train(train_no='49000K11840B', date='2016-10-28');
    one_train.query_by_train_no();
    
if __name__ == '__main__':
    main();
    
# EOF
 
    
   