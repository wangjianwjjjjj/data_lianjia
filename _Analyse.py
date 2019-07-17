# python3
# -*- coding: utf-8 -*-
__author__ = '飞鱼与熊掌'

'''
对爬取的数据进行分析
'''

import pymysql
import numpy as np
import pandas as pd
from scipy import optimize
import matplotlib.pyplot as plt


class lianjia_analyse():
    def __init__(self):
        self.data = []

    def getdata(self):
        conn = pymysql.connect(host="127.0.0.1", port=3306, user='username',
                               password='password', database='data_analyse')
        sql = '''
        select * from data_lianjia_chengjiao
        '''
        data = pd.read_sql(sql=sql,con=conn)
        self.data = data
        return True

    #多项式
    def fit_func(self,p,x):
        f = np.poly1d(p)
        return f(x)

    #误差函数
    def residuals(self,p,y,x):
        ret = self.fit_func(p,x) - y
        return ret


    def data_ana(self):
        self.getdata()

        print(self.data.goods_realprice.describe())

        size = self.data.goods_size.values #住房面积
        realprice = self.data.goods_realprice.values #住房实机成交价格
        plt.figure()
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.scatter(size,realprice)
        '''拟合曲线'''
        p_init = np.random.rand(2)
        r = optimize.leastsq(self.residuals,p_init,args=(realprice,size))
        #k,b = r[0]
        plt.plot(size,self.fit_func(r[0],size),'r')#拟合曲线
        plt.xlabel("面积（平米）")
        plt.ylabel("成交价格(万元)")
        plt.legend(['拟合曲线','散点图'],loc=2)
        plt.title('成交价格和面积之间的关系')
        plt.savefig('1.png',dpi=100)
        #plt.show()

        d = self.data[self.data.goods_realprice<=2000]
        size = d.goods_size.values
        realprice = d.goods_realprice.values
        plt.figure('修改数据后')
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.scatter(size, realprice)
        '''拟合曲线'''
        p_init = np.random.rand(2)
        r = optimize.leastsq(self.residuals, p_init, args=(realprice, size))
        k, b = r[0]
        plt.plot(size, size * k + b, 'r')  # 拟合曲线
        plt.xlabel("面积（平米）")
        plt.ylabel("成交价格(万元)")
        plt.xlim((0,500))
        plt.ylim((0,3000))
        plt.legend(['拟合曲线', '散点图'], loc=2)
        plt.title('成交价格和面积之间的关系（修改数据）')
        plt.savefig('2.png', dpi=100)
        #plt.show()

        totalprice = self.data.goods_totalprice.values #住房原价
        realprice = self.data.goods_realprice.values
        plt.figure()
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.scatter(totalprice, realprice)
        '''拟合曲线'''
        p_init = np.random.rand(2)
        r = optimize.leastsq(self.residuals, p_init, args=(realprice, totalprice))
        k, b = r[0]
        plt.plot(totalprice, totalprice * k + b, 'r')  # 拟合曲线
        plt.xlabel("原价（万米）")
        plt.ylabel("成交价格(万元)")
        plt.legend(['拟合曲线', '散点图'], loc=2)
        plt.title("实机价格和原价的关系")
        plt.savefig('3.png', dpi=100)
        #plt.show()
        #data = self.data[self.data.goods_realprice>2400]



        data = self.data[self.data.goods_dealhouseInfo!='近地铁'] #住房是否靠近地铁
        count_qita = data.shape[0]
        jdt = self.data[self.data.goods_dealhouseInfo=='近地铁'].shape[0]
        #print(count_qita,jdt)
        plt.figure()
        plt.rcParams['font.sans-serif'] = ['SimHei']
        explode = [0, 0.1]
        plt.pie([count_qita,jdt],labels=['其他','近地铁'],autopct='%1.1f%%',explode=explode)
        plt.title("住房靠近地铁和其他的所占比例")
        plt.savefig('4.png', dpi=100)
        #plt.show()



        plt.figure()
        plt.rcParams['font.sans-serif'] = ['SimHei']
        x = self.data.goods_decor.unique()  #住房装修
        x1 = self.data[self.data.goods_decor=='精装'].shape[0]
        x2 = self.data[self.data.goods_decor == '简装'].shape[0]
        x3 = self.data[self.data.goods_decor == '毛坯'].shape[0]
        x4 = self.data[self.data.goods_decor == '其他'].shape[0]
        explode = [0.1,0,0,0]
        plt.pie([x1,x2,x3,x4],labels=x,autopct='%1.1f%%',explode=explode)
        plt.title('各种住房装饰所占比例')
        plt.savefig('5.png', dpi=100)

        plt.figure()
        plt.rcParams['font.sans-serif'] = ['SimHei']
        x1 = self.data[(self.data.goods_decor=='精装')&(self.data.goods_dealhouseInfo=='近地铁')].shape[0]
        x2 = self.data[(self.data.goods_decor=='简装')&(self.data.goods_dealhouseInfo=='近地铁')].shape[0]
        x3 = self.data[(self.data.goods_decor=='毛坯')&(self.data.goods_dealhouseInfo=='近地铁')].shape[0]
        x4 = self.data[(self.data.goods_decor=='其他')&(self.data.goods_dealhouseInfo=='近地铁')].shape[0]

        x5 = self.data[(self.data.goods_decor=='精装')&(self.data.goods_dealhouseInfo!='近地铁')].shape[0]
        x6 = self.data[(self.data.goods_decor=='简装')&(self.data.goods_dealhouseInfo!='近地铁')].shape[0]
        x7 = self.data[(self.data.goods_decor=='毛坯')&(self.data.goods_dealhouseInfo!='近地铁')].shape[0]
        x8 = self.data[(self.data.goods_decor=='其他')&(self.data.goods_dealhouseInfo!='近地铁')].shape[0]

        explode = (0.1,0,0,0,0,0,0,0)
        plt.pie([x1,x2,x3,x4,x5,x6,x7,x8],autopct='%1.1f%%',explode=explode)
        plt.legend([x1,x2,x3,x4,x5,x6,x7,x8],labels=['精装 近地铁','简装 近地铁','毛坯 近地铁','其他 近地铁',
                                                  '精装 其他','简装 其他','毛坯 其他','其他 其他'],
                   bbox_to_anchor=(0.95,0.7),frameon=False)
        plt.savefig('6.png', dpi=100)
        plt.show()

if __name__ == '__main__':
    a = lianjia_analyse
    a().data_ana()