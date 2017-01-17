#-*- coding:utf-8 -*-
from django.shortcuts import render,render_to_response
from django.http import HttpResponse,Http404
from lagou.models import *
import pandas as pd
import pygal
import json
import urllib
import MySQLdb as db
#import logging
#from datetime import datetime
# Create your views here.

#主页函数
def index(request):
    svg_allByYear = allByYear()
    svg_allByQ = allByQ()
    svg_classfWithBackground = classfWithBackground()
    svg_classfWithSalary = classfWithSalary()
    svg_classTechIndus = classTechIndus()
    svg_classTechJob = classTechJob()
    svg_all_salary = userDefind_classf('salary')
    data = draws('python')
    svg_python_salary = data['salary']
    svg_pyhton_background = data['background']
    svg_pyhton_industry = data['industry']
    svg_pyhton_company = data['company']
    svg_python_allByYear = data['allByYear']
    return render(request,'index.html',locals())

#自定义查询入口
def userinfo(request):
    if request.is_ajax() and request.POST:
        care = request.POST.get('care')
        bt = request.POST.get('bt')
        bt = int(bt)
        # logging.info('查询码:%d'%bt)
        if bt==1:
            data = get_json_objects(care)
        else:
            try:
                data = draws(care)
            except ValueError,e:
                print e
        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        raise Http404()

# def page_not_found(request):
#     return render_to_response('404.html')

#按用户查询的信息读取数据库
def get_json_second(care):
    con = db.connect('localhost','root','*********','lagouwang',charset='utf8')
    sql = "select publish_time,title,jobkwd,salary,background,company,industry,classf from lagou where jobkwd like '%"+care+"%' or title like '%"+care+"%' "
    df = pd.read_sql(sql,con)
    if len(df)<=10:
        raise Http404()
    return df

#将用户查询的信息进行编码，尤其是中文，方便存储
def encodings(kw):
    return urllib.quote(kw)

#根据用户需求绘制图表
def draws(care):
    def draw(df,name,names):
        print '开始绘制%s'%name
        df1 = df.copy()
        df2 = df1.groupby(name).size().nlargest(20).reset_index()
        pie_chart = pygal.Pie()
        pie_chart.title = name
        for name,value in df2.values:
            pie_chart.add("%s:%s" % (name,value),value)
        datas = pie_chart.render_data_uri()
        svgToMysql(names,datas)
        return datas

    def allByYear(df,names):
        print '开始绘制%s'%names
        df1 = df.copy()
        df1 = df1.set_index('publish_time')
        df1.index = map(lambda x:x.strftime("%Y"),df1.index)
        s = df1.groupby([df1.index,'classf']).size()
        s2 = s.unstack()
        line_chart = pygal.Bar()
        line_chart.title = u'年度需求'
        line_chart.x_labels = s.index.levels[0]
        for p in s2.T.index:
            line_chart.add(p,s[:,p])
        datas = line_chart.render_data_uri()
        svgToMysql(names,datas)
        return datas

    name = encodings(care)
    lis = ['salary','background','industry','company','allByYear']
    finaldatas = {}
    willcal = []
    for li in lis:
        names = name+'_'+li
        findsvg = svgFromMysql(names)
        if findsvg:
            finaldatas[li]=findsvg
        else:
            willcal.append(li)

    if len(willcal)>0:
        df = get_json_second(care)
        for wi in willcal:
            names = name+'_'+wi
            if wi != 'allByYear':
                finaldatas[wi] = draw(df,wi,names)
            else:
                finaldatas['allByYear']= allByYear(df,names)
    return finaldatas

#自定义查询1的查询函数
def get_json_objects(care):
    test = userDefind_classf(care)
    svgs = {}
    svgs['svg'] = test
    return svgs

#源码展示页函数
def about(request):
    return render(request,'about.html',locals())

#个人信息展示页函数
def author(request):
    return render(request,'author.html',locals())
#从csv中读取数据
def getdf():
    df = pd.read_csv('lagouwang.csv',sep=';',index_col="publish_time",parse_dates=True,encoding="utf-8")
    return df
#将生成的图表保存到数据库
def svgToMysql(name,data):
    try:
        Svgdatas.objects.create(name=name,data=data)
    except Exception,e:
        print "insert Error"
#从数据库中查找用户需要的图表
def svgFromMysql(name):
    try:
        svg = Svgdatas.objects.filter(name=name).values('data')
        return svg[0]['data']
    except Exception,e:
        return False

def allByYear():
    findsvg = svgFromMysql("allByYear")
    if findsvg:
        return findsvg
    df1 = getdf()
    df1.index = map(lambda x:x.strftime("%Y"),df1.index)
    s = df1.groupby([df1.index,'classf']).size()
    s2 = s.unstack()
    line_chart = pygal.Bar()
    line_chart.title = u'年度职位需求'
    line_chart.x_labels = s2.index
    for p in s2.T.index:
        line_chart.add(p,s2[p])
    datas = line_chart.render_data_uri()
    svgToMysql('allByYear',datas)
    return datas

def allByQ():
    findsvg = svgFromMysql("allByQ")
    if findsvg:
        return findsvg
    df1 = getdf()
    df2 = df1.groupby([df1.index,'classf']).size().reset_index('classf').to_period(freq='Q').reset_index()
    df3 = df2.groupby(['classf','publish_time']).sum()
    df3.columns = ['counts']
    df4 = df3.reset_index()
    indexs = map(str,list(df4['publish_time']))
    s = pd.Series(list(df4.counts),index=[df4.classf,indexs])
    linechart = pygal.Line(x_label_rotation=-40)
    linechart.title=u'各职位招聘分类季度走势图'
    linechart.x_labels = s.index.levels[1]
    for i in s.index.levels[0]:
        linechart.add(i,list(s[i]))
    datas = linechart.render_data_uri()
    svgToMysql('allByQ',datas)
    return datas

def classfWithBackground():
    findsvg = svgFromMysql("classfWithBackground")
    if findsvg:
        return findsvg
    df = getdf()
    df1 = df.reset_index()
    import re
    # def bg(x):
    #     try:
    #         s = re.search('\d+-\d+|\d+',x).group()
    #         s = s+u'年'
    #     except AttributeError,e:
    #         if u'不限' in x or u'经验null' in x or u'无经验' in x:
    #             s = u'无经验'
    #         else:
    #             s=u'应届毕业生'
    #     return s
    # df1['background']=df1['background'].apply(bg)
    df2 = df1.groupby(['classf','background']).count()['title'].groupby(level=0,group_keys=False).nlargest(10)
    s = df2.unstack()
    line_chart = pygal.Bar()
    line_chart.title = u'各职位对经验的要求前十'
    line_chart.x_labels = s.index
    for p in s.T.index:
        line_chart.add(p,s[p])
    datas = line_chart.render_data_uri()
    svgToMysql('classfWithBackground',datas)
    return datas

def classfWithSalary():
    findsvg = svgFromMysql("classfWithSalary")
    if findsvg:
        return findsvg
    df = getdf()
    df1 = df.reset_index()
    df2 = df1.groupby(['classf','salary']).count()['title'].groupby(level=0,group_keys=False).nlargest(10)
    s = df2.unstack()
    line_chart = pygal.Bar()
    line_chart.title = u'各职位薪资分布前十'
    line_chart.x_labels = s.index
    for p in s.T.index:
        line_chart.add(p,s[p])
    datas = line_chart.render_data_uri()
    svgToMysql('classfWithSalary',datas)
    return datas

def classTechIndus():
    findsvg = svgFromMysql("classTechIndus")
    if findsvg:
        return findsvg
    df = getdf()
    df1 = df[df['classf']==u'技术']
    df2 = df1.groupby('industry').size().nlargest(20)
    pie_chart = pygal.Pie()
    pie_chart.title = u'技术类前20行业领域'
    for name,value in df2.iteritems():
        pie_chart.add("%s:%s" % (name,value),value)
    datas = pie_chart.render_data_uri()
    svgToMysql('classTechIndus',datas)
    return datas

def classTechJob():
    findsvg = svgFromMysql("classTechJob")
    if findsvg:
        return findsvg
    df = getdf()
    df1 = df.reset_index()
    df2 = df1[df1['classf']==u'技术']
    def bg(x):
        if x == '':
            return u'其他'
        try:
            s = x.split(',')
            t = s[0]
            i=1
            while t=='':
                t=s[i]
                i=i+1
            s=t
        except AttributeError,e:
            s=u'其他'
        return s
    df2['jobkwd']=df2['jobkwd'].apply(bg)
    df3 = df2.groupby('jobkwd').size().nlargest(20).reset_index()
    pie_chart = pygal.Pie()
    pie_chart.title = u'技术类职位数量分布'
    for name,value in df3.values:
        pie_chart.add("%s:%s" % (name,value),value)
    datas = pie_chart.render_data_uri()
    svgToMysql('classTechJob',datas)
    return datas


def changeToChinese(name):
    cn = ''
    if name == 'salary':
        cn = u'薪资'
    elif name == 'background':
        cn = u'经验'
    elif name == 'industry':
        cn = u'行业'
    elif name == 'company':
        cn = u'公司'
    else:
        cn = name
    return cn

#自定义查询2的绘图函数之一
def userDefind_classf(care):
    #df1 = df.copy()
    #df1 = df1.reset_index()
    svgName = 'class_'+care
    findsvg = svgFromMysql(svgName)
    if findsvg:
        return findsvg
    df = getdf()
    df2 = df.groupby(['classf',care]).count()['title'].groupby(level=0,group_keys=False).nlargest(10)
    radar_chart = pygal.Radar()
    radar_chart.title = changeToChinese(care)
    radar_chart.x_labels=df2.index.levels[0]
    for p in df2.index.levels[1]:
        radar_chart.add(p,df2[:,p])
    datas = radar_chart.render_data_uri()
    svgToMysql(svgName,datas)
    return datas