# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LagouwangItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #企业名称company
    #职位,关键词jobkwd
    #标题title
    #薪资salary
    #工作经验background
    #学历要求qualifications
    #公司性质industry
    #职位描述description
    #企业工作地址address
    #企业规模scale
    #企业发展阶段stage
    #企业主页companyurl
    #简历发布时间publish_time
    #职位分类classy

    company = scrapy.Field()
    jobkwd = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    background = scrapy.Field()
    industry = scrapy.Field()
    description = scrapy.Field()
    address = scrapy.Field()
    classf = scrapy.Field()
    companyurl = scrapy.Field()
    publish_time = scrapy.Field()
    pages = scrapy.Field()

