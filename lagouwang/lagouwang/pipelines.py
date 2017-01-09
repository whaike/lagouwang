# -*- coding: utf-8 -*-
import MySQLdb as db
import urllib2
from lxml import etree
from scrapy.utils.project import get_project_settings
import logging

class LagouwangPipeline(object):
    def __init__(self):
        self.DBK = get_project_settings().getdict('DBK')

    def process_item(self, item, spider):
        # logging.info('pipeline with items preparing for insert into MySQL')
        con = db.connect(self.DBK['host'],self.DBK['user'],self.DBK['passwd'],self.DBK['db'],self.DBK['port'],charset=self.DBK['charset'])
        cur = con.cursor()
        fenlei = findClassify(item['title'],item['jobkwd']).encode('utf-8')
        jobkwds = ','.join(item['jobkwd'])
        sql = ("insert into lagou(publish_time,title,jobkwd,salary,background,company,industry,companyurl,description,address,pages,classf)"
            "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
        lis = (item['publish_time'],item['title'],jobkwds,item['salary'],item['background'],item['company'],item['industry'],item['companyurl'],item['description'],item['address'],item['pages'],fenlei)
        try:
            cur.execute(sql,lis)
        except Exception,e:
            logging.info(e)
            logging.info('insert into MySQL error.................')
            con.rollback()
        else:
            con.commit()
        cur.close()
        con.close()
        logging.info('insert into MySQL over...............')
        return item

#查询并返回行业分类
def findClassify(title,kws):
    classf = {u'市场与销售': {u'高端职位': [u'市场总监', u'销售总监', u'商务总监', 'CMO', u'公关总监', u'采购总监', u'投资总监'], u'销售': [u'销售专员', u'销售经理', u'客户代表', u'大客户代表', u'BD经理', u'商务渠道', u'渠道销售', u'代理商销售', u'销售助理', u'电话销售', u'销售顾问', u'商品经理'], u'供应链': [u'物流', u'仓储'], u'公关': [u'媒介经理', u'广告协调', u'品牌公关'], u'投资': [u'分析师', u'投资顾问', u'投资经理'], u'市场/营销': [u'市场策划', u'市场顾问', u'市场营销', u'市场推广', 'SEO', 'SEM', u'商务渠道', u'商业数据分析', u'活动策划', u'网络营销', u'海外市场', u'政府关系'], u'采购': [u'采购专员', u'采购经理', u'商品经理']}, u'技术': {u'高端职位': [u'技术经理', u'技术总监', u'架构师', 'CTO', u'运维总监', u'技术合伙人', u'项目总监', u'测试总监', u'安全专家', u'高端技术职位其它'], u'运维': [u'运维工程师', u'运维开发工程师', u'网络工程师', u'系统工程师', u'IT支持', 'IDC', 'CDN', 'F5', u'系统管理员', u'病毒分析', u'WEB安全', u'网络安全', u'系统安全', u'运维经理', u'运维其它'], 'DBA': ['MySQL', 'SQLServer', 'Oracle', 'DB2', 'MongoDB', 'ETL', 'Hive', u'数据仓库', u'DBA其它'], u'项目管理': [u'项目经理', u'项目助理'], u'移动开发': ['HTML5', 'Android', 'iOS', 'WP', u'移动开发其它'], u'测试': [u'测试工程师', u'自动化测试', u'功能测试', u'性能测试', u'测试开发', u'游戏测试', u'白盒测试', u'灰盒测试', u'黑盒测试', u'手机测试', u'硬件测试', u'测试经理', u'测试其它'], u'硬件开发': [u'硬件', u'嵌入式', u'自动化', u'单片机', u'电路设计', u'驱动开发', u'系统集成', u'FPGA开发', u'DSP开发', u'ARM开发', u'PCB工艺', u'模具设计', u'热传导', u'材料工程师', u'精益工程师', u'射频工程师', u'硬件开发其它'], u'后端开发': ['Java', 'Python', 'PHP', '.NET', 'C#', 'C++', 'C', 'VB', 'Delphi', 'Perl', 'Ruby', 'Hadoop', 'Node.js', u'数据挖掘', u'自然语言处理', u'搜索算法', u'精准推荐', u'全栈工程师', 'Go', 'ASP', 'Shell', u'后端开发其它'], u'前端开发': [u'web前端', 'Flash', 'html5', 'JavaScript', 'U3D', 'COCOS2D-X', u'前端开发其它'], u'企业软件': [u'实施工程师', u'售前工程师', u'售后工程师', u'BI工程师', u'企业软件其它']}, u'产品': {u'产品设计师': [u'网页产品设计师', u'无线产品设计师'], u'高端职位': [u'产品部经理', u'产品总监', u'游戏制作人'], u'产品经理': [u'产品经理', u'网页产品经理', u'移动产品经理', u'产品助理', u'数据产品经理', u'电商产品经理', u'游戏策划', u'产品实习生']}, u'运营': {u'编辑': [u'副主编', u'内容编辑', u'文案策划', u'记者'], u'高端职位': [u'主编', u'运营总监', 'COO', u'客服总监'], u'客服': [u'售前咨询', u'售后客服', u'淘宝客服', u'客服经理'], u'运营': [u'内容运营', u'产品运营', u'数据运营', u'用户运营', u'活动运营', u'商家运营', u'品类运营', u'游戏运营', u'网络推广', u'运营专员', u'网店运营', u'新媒体运营', u'海外运营', u'运营经理']}, u'设计': {u'视觉设计': [u'网页设计师', u'Flash设计师', u'APP设计师', u'UI设计师', u'平面设计师', u'美术设计师（2D/3D）', u'广告设计师', u'多媒体设计师', u'原画师', u'游戏特效', u'游戏界面设计师', u'视觉设计师', u'游戏场景', u'游戏角色', u'游戏动作'], u'用户研究': [u'数据分析师', u'用户研究员', u'游戏数值策划'], u'高端职位': [u'设计经理/主管', u'设计总监', u'视觉设计经理/主管', u'视觉设计总监', u'交互设计经理/主管', u'交互设计总监', u'用户研究经理/主管', u'用户研究总监'], u'交互设计': [u'网页交互设计师', u'交互设计师', u'无线交互设计师', u'硬件交互设计师']}, u'职能': {u'行政': [u'助理', u'前台', u'行政', u'总助', u'文秘'], u'高端职位': [u'行政总监/经理', u'财务总监/经理', 'HRD/HRM', 'CFO', 'CEO'], u'法务': [u'法务', u'律师', u'专利'], u'人力资源': [u'人事/HR', u'培训经理', u'薪资福利经理', u'绩效考核经理', u'人力资源', u'招聘', 'HRBP', u'员工关系'], u'财务': [u'会计', u'出纳', u'财务', u'结算', u'税务', u'审计', u'风控']}, u'金融': {u'投融资': [u'投资经理', u'分析师', u'投资助理', u'融资', u'并购', u'行业研究', u'投资者关系', u'资产管理', u'理财顾问', u'交易员'], u'高端职位': [u'投资总监', u'融资总监', u'并购总监', u'风控总监', u'副总裁'], u'审计税务': [u'审计', u'法务', u'会计', u'清算'], u'风控': [u'风控', u'资信评估', u'合规稽查', u'律师']}}
    lists = kws

    #行业分类匹配
    for key in classf.keys():
        if key in title or key in lists:
            return key

    #行业中的小分类匹配
    key = ""
    for key,value in classf.items():
        for ky in value.keys():
            if ky in title or ky in lists:
                return key
    
    #职能匹配
    key = ""
    value = ""
    for key,value in classf.items():
        for ky,val in value.items():
            same = [x for x in val if x in lists or x in title]
            if len(same)>0:
                return key
    return ""


