#-*- coding:utf-8 -*-
import scrapy
import re
import datetime,time
import urllib2
from lxml import etree
from lagouwang.items import LagouwangItem
import urllib
import MySQLdb as db
from lagouwang.spiders import httpsProxys as hp
from scrapy.utils.project import get_project_settings

class lagouSpiderItem(scrapy.Spider):
    name = 'lagouSpider'
    allowed_domains = ['lagou.com']

    def __init__(self):
        print 'preparing ------------------'
        self.start_page = 1
        self.modelUrl = 'https://www.lagou.com/jobs/'
        #self.oldTime = datetime.datetime.now().hour
        self.DBK = get_project_settings().getdict('DBK') #获取settings中的DBK配置
        hp.NEWHTTPS() #准备代理IP池
        self.oldPages = self.getOldpages() #查询已插入页面列表

    def start_requests(self):
        print 'Begin--------------------'
        for page in range(self.start_page,2666666,1):
            if page not in self.oldPages:
                yield scrapy.Request(self.modelUrl+str(page)+'.html',callback=self.parse,dont_filter=True)

        #本段代码用于捡漏
        # newpages = self.getNewPages()
        # for page in newpages:
        #     yield scrapy.Request(self.modelUrl+str(page)+'.html',callback=self.parse,dont_filter=True)

    def parse(self,response):
        print response.url
        items = []
        pre_item = LagouwangItem()
        pre_item['title']= self.parseTitle(response) #职位标题
        pre_item['company'] = self.parseCompany(response)  #公司名称
        pre_item['jobkwd'] = self.parseJobkwd(response)   #职位标签 
        pre_item['salary'] = self.parseSalary(response)  #薪水 
        pre_item['background'] = self.parseBackground(response) #经验
        pre_item['industry'] = self.parseIndustry(response) #公司性质
        pre_item['description'] = self.parseDescription(response) #职位详细描述
        pre_item['address'] = self.parseAddress(response) #公司地址
        pre_item['companyurl'] = self.parseCompanyUrl(response) #公司主页
        pre_item['publish_time'] = self.parsePublishTime(response) #发布时间
        pre_item['pages'] = response.url.split('/')[-1].split('.')[0]
        items.append(pre_item)
        return items

    #解析招聘职位
    def parseTitle(self,res):
        try:
            title = res.xpath('//div[@class="position-head"]/div/div[1]/div/span/text()')[0].extract() #招聘职位
            return title
        except Exception,e:
            self.errorLog(res,'parseTitle',e)
            return ""

    #公司名称
    def parseCompany(self,res):
        company = ""
        company = str(res.xpath('//*[@id="job_company"]/dt/a/div/h2/text()').extract()[0].strip())
        return company

    #职位标签 ,返回数组
    def parseJobkwd(self,res):
        jobkwd = []
        try:
            lis = res.xpath('/html/body/div[@class="position-head"]/div/div[1]/*[@class="job_request"]/ul/li')
            if len(lis)>=1:
                for i in range(0,len(lis)):
                    job = lis[i].xpath('text()').extract()[0]
                    jobkwd.append(job)
        except Exception,e:
            self.errorLog(res,'parseJobkwd',e)
        return jobkwd

    #薪水
    def parseSalary(self,res):
        salary = ""
        try:
            salary = res.xpath('/html/body/div[@class="position-head"]/div/div[1]/dd/p[1]/span[1]/text()').extract()[0]
        except Exception,e:
            self.errorLog(res,'parseSalary',e)
        return salary

    #工作经验
    def parseBackground(self,res):
        background = ""
        try:
            background = res.xpath('/html/body/div[@class="position-head"]/div/div[1]/dd/p[1]/span[3]/text()').extract()[0].strip('/').strip()
        except Exception,e:
            self.errorLog(res,'parseBackground',e)
        return background

    #公司性质
    def parseIndustry(self,res):
        industry = ""
        try:
            industry = res.xpath('//*[@id="job_company"]/dd/ul/li[1]/text()').extract()[1].strip()
        except Exception,e:
            self.errorLog(res,'parseIndustry',e)
        return industry

    #职位详细描述
    def parseDescription(self,res):
        description = ""
        try:
            description = res.xpath('string(//*[@id="job_detail"]/dd[2])').extract()[0].encode('utf-8').strip()
        except Exception,e:
            self.errorLog(res,'parseDescription',e)
        return description

    #公司地址
    def parseAddress(self,res):
        address = ""
        try:
            address = res.xpath('string(//*[@id="job_detail"]/dd[3]/div[1])')[0].extract().strip()
            str1 = "".join(map(lambda x:x.strip() ,address.split('-')))
            address = "".join(map(lambda x:x.strip(),str1.split(' ')))[:-4:]
            # self.logger.info(address)
        except Exception,e:
            address = res.xpath('/html/body/div[@class="position-head"]/div/div[1]/dd/p[1]/span[2]/text()').extract()[0].strip('/').strip()
            self.logger.info('未找到具体地址,使用省名%s'%address)
        else:
            if '查看'==address:
                address = res.xpath('/html/body/div[@class="position-head"]/div/div[1]/dd/p[1]/span[2]/text()').extract()[0].strip('/').strip()
                self.logger.info('未找到具体地址,使用省名%s'%address)
        return address

    #公司主页
    def parseCompanyUrl(self,res):
        companyurl = ""
        try:
            companyurl = res.xpath('//*[@id="job_company"]/dd/ul/li[last()]/a/@href')[0].extract()
        except Exception,e:
            self.errorLog(res,'parseCompanyUrl',e)
        return companyurl

    #获取发布时间，并以Y-m-d形式的字符串返回
    def parsePublishTime(self,res):
        date = res.xpath('/html/body/div[@class="position-head"]/div/div[1]/dd/p[2]/text()').re('\S+')[0] #获取时间部分
        getTime = '2000-00-00'
        try:
            if re.match('\d+-\d+-\d+',date): #标准日期，直接返回字符串
                getTime = re.match('\d+-\d+-\d+',date).group()
                print getTime
            elif re.match('\d+:\d+',date): #匹配类似12:12 发布这样的格式，返回当前时间格式后的字符串
                getTime = datetime.datetime.today().strftime('%Y-%m-%d')
            elif re.match('\d+',date): #如果是类似n天前这样的时间,则取n之后与当前时间相减，格式化为字符串后返回
                dayago = int(re.match('\d+',date).group())
                getTime = (datetime.datetime.today()-datetime.timedelta(days=dayago)).strftime('%Y-%m-%d')
            else:
                getTime = '2000-00-00'
        except Exception,e:
            self.errorLog(res,'parsePublishTime',e)
        return getTime

    #获取已插入页面list
    def getOldpages(self):
        con = db.connect(self.DBK['host'],self.DBK['user'],self.DBK['passwd'],self.DBK['db'],self.DBK['port'],charset=self.DBK['charset'])
        cur = con.cursor()
        rows = []
        try:
            cur.execute("select pages from lagou")
        except Exception,e:
            print 'select error',e
        else:
            row  = cur.fetchall()
            rows = map(lambda x:int(x[0]),row)
        cur.close()
        con.close()

        t = open('E:/Python/Scrapy_test/lagouwang/301.txt','r')
        pages = t.read()
        ipss = pages.split(',')[:-1:]
        t.close()
        for i in ipss:
            if i:
                rows.append(int(i))
        if rows:
            self.logger.info('the Oldpages list is %s'%str(rows))
            return rows
        else:
            return ()

    #异常log
    def errorLog(self,res,func,e):
        self.logger.info('执行函数 %s 出错'%func)
        self.logger.info(res.url)
        self.logger.info(e)

    #用于获取那些因为超时或者没有抓取过的页面
    def getNewPages(self):
        con = db.connect(self.DBK['host'],self.DBK['user'],self.DBK['passwd'],self.DBK['db'],self.DBK['port'],charset=self.DBK['charset'])
        cur = con.cursor()
        cur.execute("select newp from newpages")
        rows = cur.fetchall()
        cur.close()
        con.close()
        pages = map(lambda x:int(x[0]),rows)
        self.logger.info('新加入页面数量:',len(pages))
        return pages