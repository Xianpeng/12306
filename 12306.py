#!/usr/bin/env python3
# coding: utf-8


import requests
import re
import json
import sys
import random
import urllib
import datetime


# disable warning
from requests.packages.urllib3.exceptions import InsecureRequestWarning,InsecurePlatformWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

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
        
    },
    'query_by_start_end':{
        'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
        'method':'GET',        
    }
}

urls={
    'queryByTrainNo':'https://kyfw.12306.cn/otn/queryTrainInfo/query?',
    'query_trainlist':'https://kyfw.12306.cn/otn/resources/js/query/train_list.js?scriptVersion=1.0',
    'get_pass_code':'https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?',
    'checkRandCodeAnsyn':'https://kyfw.12306.cn/otn/passcodeNew/checkRandCodeAnsyn',
    'query_by_start_end':'https://kyfw.12306.cn/otn/leftTicket/queryC?'
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
    def __init__(self, train_no=None, train_code=None, date=None):
        self.train_no=train_no;
        self.train_code=train_code;
        self.date=date;
        self.session=requests.Session();
        self.train_data={};        
        #if train_no is None and train_code is not None:
        #    self.train_no = self.__train_code2no(train_code);

            
    def __search_train_no_by_code(self, train_code, train_list):
        key1 = sorted(train_list.keys(),reverse=True)[0];

        for key2 in train_list[key1].keys():
            for one_train in train_list[key1][key2]:
                train_code_in_list = one_train['station_train_code'].upper();
                if train_code_in_list.find(train_code.upper()+'(') != -1:
                    train_no = train_code_in_list = one_train['train_no'];
                    return train_no;
                    
    def __train_code2no(self, train_code=None):
        if train_code is None:
            train_code = self.train_code;
            
        if train_code is None:
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
            str=resp.content;
            if str.decode().find('train_list =') != -1:
                print('查询成功');
                str_list = str.decode().split('=');
                train_list=json.loads(str_list[1]);
                # 查询成功，开始解析数据， train_list包含所有的信息
                train_no = self.__search_train_no_by_code(train_code, train_list);
                print('%s对应的NO是%s' %(train_code, train_no));
                return train_no;                
            else:
                i = i + 1;
                print('查询失败,重试第%d次' %i);
                
        return None;
        
        
    def __get_pass_code(self, module='other'):
        d = {'other':{'rand':'sjrand'}}
        if not module in d:
            print('无效的 module: %s' % (module))
            return None;
        
        s = self.session;
        my_header = common_headers;
        session_header_update(my_header, specific_headers['get_pass_code']);
        
        url = '%smodule=%s&rand=%s&' % (urls['get_pass_code'], module, d[module]['rand']);
        req=requests.Request(specific_headers['get_pass_code']['method'], url, headers=my_header);
        prepped=s.prepare_request(req);
        
        i = 0;
        while i < MAX_TRIES:
            my_header = common_headers;
            session_header_update(my_header, specific_headers['get_pass_code']);
                    
            url = '%smodule=%s&rand=%s&' % (urls['get_pass_code'], module, d[module]['rand']);
            req=requests.Request(specific_headers['get_pass_code']['method'], url, headers=my_header);
            prepped=s.prepare_request(req);            
            resp=s.send(prepped, verify=False, stream=True);
            cookies=requests.utils.dict_from_cookiejar(s.cookies);

            with open('captcha.bmp', 'wb') as fd:
                for chunk in resp.iter_content():
                    fd.write(chunk);
            print('请输入4位图片验证码(回车刷新验证码):');
            passcode = input();
        
            my_header = common_headers;
            session_header_update(my_header, specific_headers['checkRandCodeAnsyn']);
            payload={'rand':d[module]['rand'], 'randCode':passcode};
            payload=urllib.parse.urlencode(payload);
            url = '%s' % (urls['checkRandCodeAnsyn']);
            req=requests.Request(specific_headers['checkRandCodeAnsyn']['method'], url, cookies=cookies, headers=my_header, data=payload);
            prepped=s.prepare_request(req); 
            resp=s.send(prepped, verify=False);
        
            # {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"data":{"result":"1","msg":"randCodeRight"},"messages":[],"validateMessages":{}}
            obj = resp.json();
            if (obj['data']['result'] == '1'):
                print('校验验证码成功')
                return passcode
            else:
                print('校验验证码失败');
                i = i + 1;
                fd.close();
                continue  

        return None;
    
    def __query_by_train_no(self,train_no=None,date=None):
        if train_no is None:
            train_no = self.train_no;
        
        if train_no is None:
            print("Please input correct train_no");
            return None;
        
        if date is None:
            date = self.date;
        
        if date is None:
            print("请输入日期");
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
        
        train_info = resp.json();
        #print(json.dumps(train_info, indent=4));
        self.update_train_info(train_info['data']);
        
    def update_train_info(self, train_info):
        d= datetime.datetime.strptime(self.date,'%Y-%m-%d');
        
        self.train_data['number']=train_info['data'][0]['station_train_code'];
        self.train_data['begin']=train_info['data'][0]['start_station_name'];
        self.train_data['end']=train_info['data'][-1]['station_name'];
        self.train_data['date']=self.date;
        self.train_data['start-time']=self.date + ' ' + train_info['data'][0]['start_time'] + ':00';
        delta = datetime.timedelta(days=int(train_info['data'][-1]['arrive_day_diff']));
        self.train_data['arrive_time']=(d+delta).strftime('%Y-%m-%d') + ' ' + train_info['data'][-1]['arrive_time'] + ':00';
        self.train_data['via']=[];
        for station in train_info['data']:
            one_station={};
            one_station['no']=station['station_no'];
            one_station['name']=station['station_name'];
            delta = datetime.timedelta(days=int(station['arrive_day_diff']));
            one_station['arrive_time']=(d+delta).strftime('%Y-%m-%d') + ' ' + station['arrive_time'] + ':00';
            one_station['start_time']=(d+delta).strftime('%Y-%m-%d') + ' ' + station['start_time'] + ':00';
            self.train_data['via'].append(one_station);
            

    def print_train_data(self):
        print(json.dumps(self.train_data, indent=4, ensure_ascii=False));
        
    def query_by_train_code(self, train_code=None,date=None):
        train_no = self.__train_code2no(train_code);
        self.__query_by_train_no(train_no,date);

#乘客
class passenger(object):
    pass

#订单
class order(object):
    def __init__(self, from_station, to_station, date):
        self.from_station=from_station;
        self.to=to_station;
        self.date=date;
        self.session=requests.Session();
        self.trains=[];
        
    def query(self, from_station=None,to_station=None,date=None):
        if from_station is None:
            from_station = self.from_station;
        if to_station is None:
            to_station=self.to;
        if date is None:
            date = self.date;
        
        s = self.session;
        my_header = common_headers;
        session_header_update(my_header, specific_headers['query_by_start_end']);
        url = '%sleftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=ADULT' %(
            urls['query_by_start_end'],date,from_station,to_station);
        req=requests.Request(specific_headers['query_by_start_end']['method'], url, headers=my_header);
        prepped=s.prepare_request(req);
        resp=s.send(prepped, verify=False);        
        
        objs = resp.json();
        #print(json.dumps(objs, indent=4))
        for train_data in objs['data']:
            one_train={};
            one_train['from_station_no'] = train_data['queryLeftNewDTO']['from_station_no'];
            one_train['to_station_no'] = train_data['queryLeftNewDTO']['to_station_no'];
            one_train['train_code']=train_data['queryLeftNewDTO']['station_train_code'];
            train_info=train(train_code=train_data['queryLeftNewDTO']['station_train_code'], date=date);
            train_info.query_by_train_code();
            one_train['train_info']=train_info;
            self.trains.append(one_train);
        
        print("所有车次")
        for train_info in self.trains:
            print(train_info['train_code']);

def main():
    #one_train=train(train_no='49000K11840B', date='2016-10-28');
    #one_train.query_by_train_code('K1184','2016-10-28');
    #one_train.print_train_data();
    myorder=order('SHH','LSO','2016-10-28');
    myorder.query();
    
if __name__ == '__main__':
    main();
    
# EOF
 
    
   