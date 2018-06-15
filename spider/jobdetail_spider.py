
import logging
import os

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from config.config import TIME_SLEEP

from util.excel_helper import mkdirs_if_not_exists

JOB_DETAIL_DIR = './data/'

logging.basicConfig(format="%(asctime)s-%(name)s-%(levelname)s-%(message)s\t", level=logging.DEBUG)

# 爬取工作详细信息
def crawl_job_detail(positionId, positionName):
    request_url = 'https://m.lagou.com/jobs/' + str(positionId) + '.html'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Host': 'm.lagou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4'
    }

    response = requests.get(request_url, headers=headers, timeout=10)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html5lib')

        items = soup.find('div', class_='items')
        jobnature = items.find('span', class_='item jobnature').span.text.strip()
        workyear = items.find('span', class_='item workyear').span.text.strip()
        education = items.find('span', class_='item education').span.text.strip()
        jd = soup.find_all('div', class_='content')[0].get_text().strip().replace('\n', '').replace('&nbps;', '')  # jd

        
        #　休眠２s
        time.sleep(TIME_SLEEP)
    elif response.status_code == 403:
        logging.error('request is forbidden by the server...')
    else:
        logging.error(response.status_code)

    return [positionId, positionName, jobnature, workyear, education, jd]

# 将工作详细信息写入文件
def write_job_details_to_txt(positionId, text, parent_dir_name):
    details_dir = JOB_DETAIL_DIR + parent_dir_name + os.path.sep
    mkdirs_if_not_exists(details_dir)
    try:
        f = open(details_dir + str(positionId) + '.txt', mode='w', encoding='UTF-8')
    except:
        import io
        f = io.open(details_dir + str(positionId) + '.txt', mode='w', encoding='UTF-8')
    finally:
        f.write(text)
        f.flush()
        f.close()
        logging.info('%s has been written successfully...' % positionId)

# 保存职位详细信息
if __name__ == '__main__':
    for excel_file in os.listdir(JOB_DETAIL_DIR):
        df = pd.read_excel(os.path.join(JOB_DETAIL_DIR, excel_file), index_col=False)

        jd_item_list = list()
        for _ in range(len(df)):
            positionId = df['职位编码'].tolist()[_]
            positionName = excel_file.replace('.xlsx', '')
            try:
                jd_item = crawl_job_detail(positionId, positionName)
                print(jd_item)
                jd_item_list.append(jd_item)
            except:
                pass
        # 列名
        col = [
            u'职位编码',
            u'职位类型',
            u'工作性质',
            u'工作经验',
            u'教育程度',
            u'详情描述']
        df = pd.DataFrame(jd_item_list, columns=col)
        # 保存路径和文件名
        path = "./data/"
        df.to_excel(path + positionName + "-JD.xlsx", sheet_name=positionName, index=False, encoding='UTF-8')
