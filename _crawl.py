from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import pymysql
import time
import random


class lianjia_crawl():
    #模拟浏览器的准备
    def __init__(self,url):
        self.url = url
        self.data = []
        self.errordata = []
        self.i = 0
        self.options = webdriver.ChromeOptions() #添加一些额外的设置
        #添加请求头
        self.options.add_argument('user-agent="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, '
                                  'like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60Opera/8.0 '
                                  '(Windows NT 5.1; U; en)"')
        #禁止加载图片，减少加载时间
        self.options.add_experimental_option("prefs", {"profile.mamaged_default_content_settings.images": 2})
        #开发者选项
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.browser = webdriver.Chrome(options = self.options)
        self.wait = WebDriverWait(self.browser,20)
        self.browser.get(self.url)
        time.sleep(5+random.random())

    def net_page(self):  #模拟点击下一页
        #等待点击对象加载出现
        next_buttom = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'.content > .leftContent > .contentBottom > .page-box > '
                                                            '.house-lst-page-box > a:last-child'))
        )
        time.sleep(3+random.random())
        #模拟鼠标滑动
        self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight-426);")
        time.sleep(2+random.random())
        next_buttom.click()
    #爬取总页数
    def getPage(self):
        # goods_tatol = self.wait.until(EC.presence_of_element_located(
        #     (By.CSS_SELECTOR,'.content > .leftContent > .sellListContent > .clear > .info')
        # ))
        goods_tatol = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.content > .leftContent > .sellListContent > .clear > .info')
        ))
        self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight);")

        page_total = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'.content > .leftContent > .contentBottom > .page-box > '
                                                            '.house-lst-page-box > a:nth-child(5)'))
        )
        result = page_total.text
        return result

    def get_info(self):
        list_info = []
        total_page = self.getPage()
        print(total_page)

        for i in range(1,int(total_page)+1):
            goods_tatol = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '.content > .leftContent > .sellListContent > .clear > .info')
            ))

            #通过pyquery来解析网页，得到你想要的数据
            html = self.browser.page_source
            doc = pq(html)
            goods_items = doc('.content .leftContent .sellListContent .clear .info').items()
            for item in goods_items:
                try:
                    goods_title = item.find('.title a').text().replace(" ", "")
                    goods_address = item.find('.address .houseInfo').text().split('|')

                    goods_add = goods_address[0].replace(" ", "")
                    goods_housetype = goods_address[1].replace(" ", "")
                    goods_size = float(goods_address[2].replace(" ", "").replace("平米", ""))
                    goods_orientation = goods_address[3].replace(" ", "")
                    goods_decor = goods_address[4].replace(" ", "")

                    goods_position = item.find('.flood .positionInfo').text().replace(" ", "") + "-" + goods_add
                    goods_star1 = item.find('.followInfo').text().split("/")
                    goods_star = float(goods_star1[0].replace(" ", "").replace("人关注", ""))
                    goods_totalprice = float(
                        item.find('.priceInfo .totalPrice').text().replace(" ", "").replace("万", ""))
                    goods_perprice = float(
                        item.find('.priceInfo .unitPrice').text().replace(" ", "").replace("单价", "").replace("元/平米",
                                                                                                           ""))
                    self.i = self.i + 1
                    list_info.append(
                        [self.i,goods_title, goods_position, goods_size, goods_housetype, goods_orientation, goods_decor,
                         goods_star, goods_totalprice, goods_perprice])
                except:
                    self.errordata.append(item)
                    print("error info:",item)
                    continue

            self.net_page()

        self.data = list_info
        time.sleep(2+random.random())
        self.browser.close()
        return list_info

    def write_to_mysql(self):
        conn = pymysql.connect(host="127.0.0.1",port=3306,user='用户名',password='你的数据库密码',database='数据库名')
        cursor = conn.cursor()
        #初始化
        table_init ="drop table if exists data_lianjia"
        cursor.execute(table_init)
        conn.commit()
        #创建表
        creat_table = '''
                create table if not exists data_lianjia(
                id int primary key not null ,
                goods_title varchar(50) ,
                goods_position varchar(100) ,
                goods_size float ,
                goods_housetype varchar (50) ,
                goods_orientation varchar(20) ,
                goods_decor varchar(50) ,
                goods_star float ,
                goods_totalprice float ,
                goods_perprice float 
                )
                '''
        cursor.execute(creat_table)
        conn.commit()

        data = []
        for line in self.data:
            data.append(tuple(line))
        data = tuple(data)
        #添加数据
        insert_data = '''
        insert into data_lianjia values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        '''
        cursor.executemany(insert_data,data)
        conn.commit()
        cursor.close()
        conn.close()
        return True


if __name__ == '__main__':
    url = 'https://bj.lianjia.com/ershoufang/'
    s = lianjia_crawl(url)
    # s.getPage()
    s.get_info()
    s.write_to_mysql()
