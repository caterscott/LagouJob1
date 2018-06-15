import time

from util import log
from config import config
import os
from spider import m_lagou_spider

import requests
from bs4 import BeautifulSoup
import pandas as pd

    # 爬取公司详细信息：
S = './company'


def crawl_company(havemark=0):


    # 　定义公司信息为列表形式
    COMPANY_LIST = list()
    # 请求的url
    req_url = 'https://www.lagou.com/gongsi/0-0-0.json?havemark=%d' % havemark
    # 请求头部
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'www.lagou.com',
        'Origin': 'https://www.lagou.com',
        'Referer': 'https://www.lagou.com/gongsi/0-0-0?havemark=0',
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 '
                      'Mobile/13B143 Safari/601.1'
    }

    #  进行页数循环
    for pn in range(20):
        params = {
            'first': 'false',
            'pn': str(pn),
            'sortField': '0',
            'havemark': str(havemark)
        }

        response = requests.post(req_url, headers=headers, params=params, cookies=m_lagou_spider.get_cookies(),
                                 timeout=10)
        print(response.url)
        if response.status_code == 200:
            company_list_per_page = response.json()['result']
            for company in company_list_per_page:
                COMPANY_LIST.append([company['companyId'], company['companyShortName'],
                                     company['city'], company['companyFeatures'],
                                     company['companyFullName'], company['financeStage'], company['industryField'],
                                     company['interviewRemarkNum'], company['positionNum'], company['processRate']])
            log.info('page %d has been crawled down~' % (pn + 1))
        elif response.status_code == 403:
            log.error('403 forbidden...')
        else:
            log.error(response.status_code)
        # 睡眠
        time.sleep(config.TIME_SLEEP)

    return COMPANY_LIST

    # 爬取公司信息
def crawl_company_stage(company_id):
    # 请求url
    req_url = 'https://m.lagou.com/gongsi/%s.html' % str(company_id)
    # 请求头
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Host': 'm.lagou.com',
        'Referer': 'https://m.lagou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
    }
    # 发送请求，cookie为m_lagou_spider的cookie，即为第一次登陆时的cookie
    response = requests.get(req_url, headers=headers, cookies=m_lagou_spider.get_cookies(), timeout=20)
    # 打印出响应的url
    print(response.url)
    # 如果返回200，使用Beautifulsoup爬取各部分内容
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html5lib')
        company_desc = soup.find_all(class_="desc")[0].get_text().strip()
        industryField = company_desc.split('/')[0].strip()
        financeStage = company_desc.split('/')[1].strip()
        staffNum = company_desc.split('/')[2].strip()
    # 如果返回403，打印出以下信息
    elif response.status_code == 403:
        log.error('403 forbidden...')
    else:
        log.error(response.status_code)
    # 休眠2s
    time.sleep(config.TIME_SLEEP)
    # 返回列表
    return [company_id, industryField, financeStage, staffNum]

    # 保存公司详细内容
if __name__ == '__main__':
    company_level_list = list()
    visited_company_id_list = list()
    # os.listdir('./data')返回data文件夹文件名列表
    for job in os.listdir('./data'):
        # 取出工作列表中的公司编码，进行循环
        for company_id in pd.read_excel(os.path.join('./data', job))['公司编码']:
            # 若公司id不存在于列表中，
            if not company_id in visited_company_id_list:
                try:
                    company = crawl_company_stage(company_id)
                    company_level_list.append(company)
                    visited_company_id_list.append(company_id)
                except:
                    pass
                finally:
                    # 公司内容列表
                    cols = [u'公司编码', u'所属行业', u'融资阶段', u'员工数量']
                    df = pd.DataFrame(company_level_list, columns=cols)
                    # 保存路径及格式
                    df.to_excel('%s/company.xlsx' % S, 'Company', index=False)
            else:
            # 若存在列表中，则显示一下信息
                log.info('%d has been visited before...' % company_id)
    log.info('Processing done!')

    # company_list = crawl_company(0)
    # cols = [u'公司编码', u'公司名称', u'所在城市', u'企业文化', u'公司全称', u'融资阶段', u'所属行业', u'面试评价', u'在招职位', u'简历处理速率']
    # df = pd.DataFrame(company_list, columns=cols)
    # df.to_excel('./data/company.xlsx', 'Company', index=False)
    # log.info('Processing done!')
