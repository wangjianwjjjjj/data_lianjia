# python3
# -*- coding: utf-8 -*-
__author__ = '飞鱼与熊掌'

'''
爬取链家北京地区已经交易的房家信息
'''

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import pymysql
import time
import random


class lianjia_crawl():
    def __init__(self, url):
        self.url = url
        self.data = []
        self.errordata = []
        self.i = 0
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('user-agent="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, '
                                  'like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60Opera/8.0 '
                                  '(Windows NT 5.1; U; en)"')
        self.options.add_experimental_option("prefs", {"profile.mamaged_default_content_settings.images": 2})
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.browser = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.browser, 20)
        self.browser.get(self.url)
        time.sleep(5 + random.random())

    def net_page(self):
        next_buttom = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.content > .leftContent > .contentBottom > .page-box > '
                                                             '.house-lst-page-box > a:last-child'))
        )
        time.sleep(3 + random.random())
        self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight-426);")
        time.sleep(2 + random.random())
        next_buttom.click()

    def getPage(self):
        # goods_tatol = self.wait.until(EC.presence_of_element_located(
        #     (By.CSS_SELECTOR,'.content > .leftContent > .sellListContent > .clear > .info')
        # ))
        goods_tatol = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.content > .leftContent > .listContent')
        ))
        self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight);")

        page_total = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.content > .leftContent > .contentBottom > .page-box > '
                                                             '.house-lst-page-box > a:nth-child(5)'))
        )
        result = page_total.text
        return result

    def get_info(self):
        list_info = []
        total_page = self.getPage()
        print(total_page)

        for i in range(1, int(total_page)+1):
            # goods_tatol = self.wait.until(EC.presence_of_element_located(
            #     (By.CSS_SELECTOR, '.content > .leftContent > .sellListContent > .clear > .info')
            # ))
            goods_tatol = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.content > .leftContent > .listContent')
            ))
            html = self.browser.page_source
            doc = pq(html)
            # goods_items = doc('.content .leftContent .sellListContent .clear .info').items()
            goods_items = doc('.content .leftContent .listContent .info').items()
            for item in goods_items:
                try:

                    goods_title = item.find('.title a').text().split(' ')

                    goods_add = goods_title[0].replace(" ", "")
                    goods_housetype = goods_title[1].replace(" ", "")
                    goods_size = float(goods_title[2].replace(" ", "").replace("平米", ""))

                    goods_t = item.find('.address .houseInfo').text().replace(" ","").split("|")
                    goods_orientation = goods_t[0].replace(" ", "")
                    goods_decor = goods_t[1].replace(" ", "")
                    goods_realprice = float(item.find('.address .totalPrice').text().replace("万",""))
                    #住房成交价格
                    
                    goods_position = item.find('.flood .positionInfo').text().replace(" ", "") + "-" + goods_add
                    goods_unitPrice = float(item.find('.flood .unitPrice').text().replace(" ","").replace("元/平",""))
                    #住房平均价格
                    try:
                        goods_dealhouseInfo = item.find('.dealHouseInfo .dealHouseTxt span:nth-child(2)').text(). \
                            replace(" ", "").replace("/", "")
                    except:
                        goods_dealhouseInfo = []
                        print("error info:", item,"\n")


                    goods_totalprice = float(
                        item.find('.dealCycleeInfo .dealCycleTxt span:nth-child(1)').text().replace(" ", "").
                            replace("万", "").replace("挂牌",""))
                    #住房发布价格
                    #
                    self.i = self.i + 1
                    list_info.append(
                        [self.i , goods_dealhouseInfo,goods_position, goods_size, goods_housetype, goods_orientation,
                         goods_decor, goods_totalprice,goods_realprice,goods_unitPrice])
                except:
                    self.errordata.append(goods_title)
                    print("error info:", item,"\n")
                    continue

            self.net_page()

        self.data = list_info
        time.sleep(2 + random.random())
        self.browser.close()
        return list_info

    def write_to_mysql(self):
        conn = pymysql.connect(host="127.0.0.1", port=3306, user='用户名', password='用户密码', database='数据库名')
        cursor = conn.cursor()
        table_init = "drop table if exists data_lianjia_chengjiao"
        cursor.execute(table_init)
        conn.commit()

        creat_table = '''
                create table if not exists data_lianjia_chengjiao(
                id int primary key not null ,
                goods_dealhouseInfo varchar(20) ,
                goods_position varchar(100) ,
                goods_size float ,
                goods_housetype varchar (50) ,
                goods_orientation varchar(20) ,
                goods_decor varchar(50) ,
                goods_realprice float ,
                goods_totalprice float ,
                goods_unitPrice float 
                )
                '''
        cursor.execute(creat_table)
        conn.commit()

        data = []
        for line in self.data:
            data.append(tuple(line))
        data = tuple(data)
        insert_data = '''
        insert into data_lianjia_chengjiao values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        '''
        cursor.executemany(insert_data, data)
        conn.commit()
        cursor.close()
        conn.close()
        return True


if __name__ == '__main__':
    url = 'https://bj.lianjia.com/chengjiao/'
    s = lianjia_crawl(url)
    # s.getPage()
    s.get_info()
    s.write_to_mysql()