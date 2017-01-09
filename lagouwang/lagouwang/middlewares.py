#-*- coding:utf-8 -*-
from scrapy.exceptions import IgnoreRequest
import MySQLdb as db
import base64
import random
from settings import USER_AGENTS
from scrapy.utils.project import get_project_settings
from lagouwang.spiders import httpsProxys as hp
import logging
import time

#选择随机user-agent
class RandomUserAgent(object):
    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', random.choice(USER_AGENTS))

#添加代理
class ProxyMiddleware(object):
    def process_request(self,request,spider):
        https_proxy = 'https://'+Sup.getRandomIp()
        request.meta['proxy'] = https_proxy

#如果返回301则丢弃，其他不正常的状态码全部重新来过
#301 - 空页面没有招聘信息
#302 - 被重定向到禁止页面，也就是该代理地址被ban了
#404 - 空页面没有招聘信息 ：本网站的Coder和PM私奔啦~~~
class CheckResponse(object):
    def process_response(self,request,response,spider):
        logging.info('response url %s with proxy:%s got status %s '%(response.url,request.meta['proxy'],response.status))
        if response.status != 200:
            if response.status == 301 or response.status == 404:
                Sup.letpagesgo(response.url)
                raise IgnoreRequest('found no pages')
            else:
                Sup.deleteProxy(request)
                new_request = request.copy()
                new_request.dont_filter = True
                return new_request
        else:
            return response

    #删除伴随异常的代理IP
    def process_exception(self,request,exception,spider):
        try:
            Sup.deleteProxy(request)
        except Exception,e:
            print e

#代理辅助
class Sup(object):
    DBK = get_project_settings().getdict('DBK')
    NUM_PONDS = get_project_settings().getint('NUM_PONDS') #IP池大小
    proxy_pond = [] #IP池
    proxy_id = [] #IP池中的IP对应在数据库中的id号

    #如果IP池子空了，则调用updateProcyPond更新池子
    @classmethod
    def getRandomIp(self):
        if len(self.proxy_pond)<1:
            self.updateProxyPond()
        return random.choice(self.proxy_pond)
    @classmethod
    def deleteProxy(self,request):
        try:
            proxyIp = request.meta['proxy']
            willdelete = proxyIp.split('//')[1]
            if willdelete in self.proxy_pond:
                self.proxy_pond.remove(willdelete)
                logging.info('delete proxy %s'%willdelete)
            else:
                logging.info("the proxy %s was deleted which not in proxy_pond"%willdelete)
            logging.info('动态IP池剩余IP数:%s'%len(self.proxy_pond))
        except Exception,e:
            logging.info(e)
            logging.info('delete proxy ip from proxy_pond error')

    #如果池子中的IP都已经用完，且不可使用，则从数据库中删除，然后重新补充IP池子
    @classmethod
    def updateProxyPond(self):
        con = db.connect(self.DBK['host'],self.DBK['user'],self.DBK['passwd'],self.DBK['db'],self.DBK['port'],charset=self.DBK['charset'])
        cur = con.cursor()
        if len(self.proxy_id)>0:
            logging.info('需要清理id个数为...%s'%len(self.proxy_id))
            for di in self.proxy_id:
                sql = "delete from xiciproxy where id = %d"%di
                try:
                    cur.execute(sql)
                except Exception,e:
                    logging.info('delete ip error')
            con.commit()
        limis = "select id,ip from xiciproxy limit %d"%self.NUM_PONDS
        cur.execute(limis)
        gots = cur.fetchall()
        if len(gots)<5:
            print "proxy IP in db is not enough ,please run 'httpsProxys.py' to get more proxy ip address !"
            logging.info('数据库代理IP不够用了,正在休眠等待抓取...')
            time.sleep(300)
        self.proxy_id = map(lambda tp:int(tp[0]),gots)
        self.proxy_pond = map(lambda tp:tp[1],gots)
        cur.close()
        con.close()

    @classmethod
    def letpagesgo(self,url):
        page1 = url.split('/')[-1].split('.')[0]
        # if int(page1) not in self.oldPages:
        page2 = page1+','
        f = open('301.txt','a')
        f.writelines(page2)
        f.close()


