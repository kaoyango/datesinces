# -*- coding: utf-8 -*
import re
from bs4 import BeautifulSoup
import time
from selenium import webdriver
import os
import pandas as pd


#启动测试浏览器
driver = webdriver.Firefox()
driver.implicitly_wait(10)


#进入拉勾网首页，完成手动登录
def login_in():
    homepage = 'https://www.lagou.com/'
    driver.get(homepage)

    print("请在30秒内完成以下操作：")
    print("1.选择全国站")
    print("2.点击登录：输入你的账号&密码")
    # account =
    # password =

    time.sleep(30)


#翻页拿目录
def getdata_turnpage():

    url = 'https://www.lagou.com/zhaopin/shujufenxishi/'  #全国站>设计>用户研究>数据分析师的入口url

    driver.get(url)
    time.sleep(2)
    htm = driver.page_source
    htm = re.sub(r'\n|\t|\  ', '', htm)
    sou = BeautifulSoup(htm, 'lxml')
    t = sou.find(class_='pager_container').select('a')[-2].text  #获取翻页页数
    t = int(t)+1

    positionlist = []

    for i in range(1,t): #翻页
        print("当前页：{}".format(str(i)))

        turl = url + str(i) + '/'

        driver.get(turl)
        time.sleep(1)
        html = driver.page_source
        html = re.sub(r'\n|\t|\  ', '', html)
        soup = BeautifulSoup(html, 'lxml')
        contents = soup.find(class_='s_position_list').find(class_='item_con_list').find_all(class_='con_list_item default_list')

        for content in contents:
            try:
                company = content.find(class_='company').find(class_='company_name').text
                company = re.sub(r'该企业已上传营业执照并通过资质验证审核','',company)
            except:
                company = ''

            try:
                position = content.find(class_='position').find(class_='p_top').find(class_='position_link').text
                position = re.sub(r'\[.*','',position)
            except:
                position = ''

            try:
                pubdate = content.find(class_='position').find(class_='p_top').find(class_='format-time').text
                pubdate = re.sub(r'发布','',pubdate)
            except:
                pubdate = ''

            try:
                positionlink = content.find(class_='position').find(class_='position_link').attrs['href']
            except:
                positionlink = ''

            jsondata = {}

            jsondata['company'] = company
            jsondata['position'] = position
            jsondata['pubdate'] = pubdate
            jsondata['positionlink'] = positionlink
            positionlist.append(jsondata)

    return positionlist


#获取详情页信息
def getitemdetails(data): #传入dict

    joblabels = salary = salary_min = salary_max = city = experience = education = fulltime = ''
    positionlabels = p_label1 = p_label2 = p_label3 = p_label4 = p_label5 = p_label6 = ''
    advantage = description = address = field = develop_stage = scale = company_website = ''

    purl = data['positionlink']
    driver.get(purl)
    time.sleep(1)
    htm2 = driver.page_source
    htm2 = re.sub(r'\n|\r|\t|\  ','',htm2)
    soup = BeautifulSoup(htm2,'lxml')

    try:
        joblabels = soup.find(class_='job_request').p.select('span')
    except Exception as e:
        print(e)
        print('joblabels出现问题')

    try:
        salary = joblabels[0].text
    except:
        pass

    try:
        salary_min = re.sub(r'-.*', '', salary)
        salary_min = re.sub(r' ', '', salary_min)
        salary_min = salary_min.rstrip('k')
        salary_min = salary_min.rstrip('K')
        salary_min = float(salary_min)
    except:
        pass

    try:
        salary_max = re.sub(r'.*-', '', salary)
        salary_max = re.sub(r' ', '', salary_max)
        salary_max = salary_max.rstrip('k')
        salary_max = salary_max.rstrip('K')
        salary_max = float(salary_max)
    except:
        pass

    try:
        city = joblabels[1].text
        city = re.sub(r'/','',city)
    except:
        pass

    try:
        experience = joblabels[2].text
        experience = re.sub(r'/', '', experience)
    except:
        pass

    try:
        education = joblabels[3].text
        education = re.sub(r'/', '', education)
    except:
        pass

    try:
        fulltime = joblabels[4].text
    except:
        pass

    try:
        positionlabels = soup.find(class_='job_request').find(class_='position-label').select('li')
    except Exception as e:
        print(e)
        print('positionlabels出现问题')

    try:
        p_label1 = positionlabels[0].text
    except:
        pass

    try:
        p_label2 = positionlabels[1].text
    except:
        pass

    try:
        p_label3 = positionlabels[2].text
    except:
        pass

    try:
        p_label4 = positionlabels[3].text
    except:
        pass

    try:
        p_label5 = positionlabels[4].text
    except:
        pass

    try:
        p_label6 = positionlabels[5].text
    except:
        pass

    try:
        advantage = soup.find(class_='job_detail').find(class_='job-advantage').text
        advantage = re.sub(r'职位诱惑：', '', advantage)
    except:
        pass

    try:
        description = soup.find(class_='job_detail').find(class_='job_bt').div.text
    except:
        pass

    try:
        address = soup.find(class_='job-address').find(class_='work_addr').text
        address = re.sub(r'查看地图', '', address)
    except:
        pass

    try:
        for inf in soup.find(class_='content_r').find(class_='job_company').find(class_='c_feature').select('li'):
            if inf.text.find('领域') != -1:
                field = re.sub(r'领域', '', inf.text)
                field = field.lstrip(' ')
    except:
        pass

    try:
        for inf in soup.find(class_='content_r').find(class_='job_company').find(class_='c_feature').select('li'):
            if inf.text.find('发展阶段') != -1:
                develop_stage = re.sub(r'发展阶段', '', inf.text)
                develop_stage = develop_stage.lstrip(' ')
    except:
        pass

    try:
        for inf in soup.find(class_='content_r').find(class_='job_company').find(class_='c_feature').select('li'):
            if inf.text.find('规模') != -1:
                scale = re.sub(r'规模', '', inf.text)
                scale = scale.lstrip(' ')
    except:
        pass

    try:
        for inf in soup.find(class_='content_r').find(class_='job_company').find(class_='c_feature').select('li'):
            if inf.text.find('公司主页') != -1:
                company_website = inf.a.attrs['href']
    except:
        pass

    data['salary'] = salary
    data['salary_min(k)'] = salary_min
    data['salary_max(k)'] = salary_max
    data['city'] = city
    data['experience'] = experience
    data['education'] = education
    data['fulltime'] = fulltime
    data['p_label1'] = p_label1
    data['p_label2'] = p_label2
    data['p_label3'] = p_label3
    data['p_label4'] = p_label4
    data['p_label5'] = p_label5
    data['p_label6'] = p_label6
    data['advantage'] = advantage
    data['description'] = description
    data['address'] = address
    data['field'] = field
    data['develop_stage'] = develop_stage
    data['scale'] = scale
    data['company_website'] = company_website

    print(data)
    return data


#数据导出
def convert_excel(datas):
    name1 = '拉勾网_数据分析师_全国'
    xls_name = name1 + '(' + str(time.strftime('%Y%m%d', time.localtime(time.time())))+ ')' + '.xlsx'
    exp_file_name = os.path.join('E:/', xls_name)
    writer = pd.ExcelWriter(exp_file_name)

    df = pd.DataFrame(datas)
    df.to_excel(writer, columns=['company','position','pubdate','positionlink','salary','salary_min(k)','salary_max(k)',
                                 'city','experience','education','fulltime','p_label1','p_label2','p_label3','p_label4','p_label5','p_label6',
                                 'advantage','description','address','field','develop_stage','scale','company_website'], index=False)
    writer.save()
    writer.close()
    print("数据导出成功，在E盘文件夹")


#程序入口
if __name__ == '__main__':
    start_time = time.time()

    login_in()
    datalist = getdata_turnpage()
    enddatats = []
    z = 1
    for jsondata in datalist:
        print("当前数据：{}".format(str(z)))
        try:
            enddatats.append(getitemdetails(jsondata))
        except Exception as e:
            print(e)
            print(jsondata)
        z += 1

    driver.close()

    end_time = time.time()
    print('数据处理结束，用时%.5f秒' % (end_time - start_time))
convert_excel(enddatats)