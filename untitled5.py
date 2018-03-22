# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 08:53:38 2018

@author: Administrator
"""

import pandas as pd
import datetime
import re
from urllib.parse import quote
from urllib.request import urlopen
import json
def getScaleNumber(ticket):
    match = re.compile("([\d]+)人").search(ticket)
    match1 = re.compile("([\d]+)-([\d]+)人").search(ticket)
    if match1:
        return (int(match1.group(1))+int(match1.group(2)))/2
    elif match:
        return 2001 if int(match.group(1))==2000 else 2
    else:
        '0'
def getlnglat(address):
    """根据传入地名参数获取经纬度"""
    url = 'http://api.map.baidu.com/geocoder/v2/'
    output = 'json'
    ak = 'EzdVOO7lhqTpgaES8l7zIiGuLW4laNUS'
    add = quote(address) 
    uri = url + '?' + 'address=' + add  + '&output=' + output + '&ak=' + ak 
    req = urlopen(uri)
    res = req.read().decode() 
    temp = json.loads(res)
    lat=temp['result']['location']['lat']
    lng=temp['result']['location']['lng']
    return lat,lng
sj=pd.read_excel('拉勾网_数据分析师_全国(20180318).xlsx',head=0)
#清除没给薪资的数据
sj.drop(sj[sj['salary'].isnull()].index,inplace=True)
#清洗时间格式为2天前或11:23时间为同一时间格式
sj['pubdate']=sj['pubdate'].replace(r'[0-9]\d*:[0-9]\d*','0天前',regex=True)
sj['newpubdate']=sj['pubdate'][sj['pubdate'].str.endswith('天前',na=True)].map(lambda x:\
(datetime.datetime(2018, 3, 18)-datetime.timedelta(days=int(x[0]))).strftime('%Y-%m-%d'))
sj['pubdate']=sj['newpubdate'].combine_first(sj['pubdate'])
sj['pubdate']=sj['newpubdate'].combine_first(sj['pubdate'])
sj.drop(['newpubdate'],axis=1,inplace=True)
sj['pubdate'] = pd.to_datetime(sj['pubdate'])
#时间格式设为索引
sj.set_index('pubdate',inplace=True)
#以工作日为时间轴看薪资变化趋势
sj.resample('B',how='mean').plot()
#给薪资和企业人数分个区间
sj['price']=pd.cut((sj['salary_min(k)']+sj['salary_max(k)'])/2, 10)
sj['scale']=pd.cut(sj['scale'].map(lambda x:getScaleNumber(str(x))).astype('float',errors='ignore'),\
[0,15,50,150,500,2000,9999])
#经验和学历的哑变化
experience = pd.get_dummies(sj['experience']).rename(columns=lambda x: 'experience_'+x[2:])
education = pd.get_dummies(sj['education']).rename(columns=lambda x: 'education'+x[:2])
sj['experience_id'] = pd.factorize(sj['experience'])[0]+1
sj['education_id'] = pd.factorize(sj['education'])[0]+1
sj = pd.concat([sj, experience, education], axis=1)
#最小薪资与企业规模和学历关系
sj['salary_min(k)'].groupby([sj['scale'],sj['experience_id']]).mean().unstack()
#百度地图
AK='EzdVOO7lhqTpgaES8l7zIiGuLW4laNUS'
sj['local']=sj['address'].map(lambda x:getlnglat(x))
