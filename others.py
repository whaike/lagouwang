# -*- encoding: utf-8 -*-
import MySQLdb as db

#获取所有分类信息,以字典形式返回
# classf = getClassify()
def getClassify():
    url = 'https://www.lagou.com/'
    data = urllib2.urlopen(url).read().decode('utf-8')
    html = etree.HTML(data)
    classify = {}
    try:
        for i in range(8):
            fenlei = html.xpath('//*[@id="sidebar"]/div[%s]/div'%i)
            for j in range(0,len(fenlei)):
                tech = fenlei[j].xpath('div[1]/h2/text()')[0].strip()
                classify[tech] = {}
                techs = fenlei[j].xpath('div[2]/dl')
                for k in range(0,len(techs)):
                    tech_name = techs[k].xpath('dt/a/text()')[0].strip()
                    tech_name_items = techs[k].xpath('dd/a/text()')
                    items = []
                    for l in range(0,len(tech_name_items)):
                        items.append(tech_name_items[l])
                    classify[tech][tech_name]=items
    except Exception,e:
        print e
    return classify

#查询数据库中还剩多少IP
def getProxysNumberFromDB():
	con = db.connect('localhost','root','********','lagouwang',charset='utf8')
	cur = con.cursor()
	cur.execute('select count(ip) from xiciproxy')
	rows = cur.fetchone()
	print rows
	print('数据库中的代理ip还剩下 %d 个'%int(rows[0]))
	cur.close()
	con.close()

#获取漏掉的页面并写入数据库(将301.txt复制到当前目录下)
def getOtherPages():
	with open('./lagouwang/301.txt') as f:
		s = f.read()
	txt = map(lambda x:int(x),s.split(',')[:-1])
	falsePgs = list(set(txt))
	print '失败页面长度:',len(falsePgs)

	con = db.connect('localhost','root','*******','lagouwang',charset='utf8')
	cur = con.cursor()
	cur.execute('select pages from lagou')
	rows = cur.fetchall()
	cur.close()
	con.close()
	pages = map(lambda x:int(x[0]),rows)
	print '成功页面的长度:',len(pages)

	oldPage = sorted(list(set(falsePgs+pages)))
	print '合并+排序后总长度:',len(oldPage)
	print '正在计算未处理页面...'
	result = range(oldPage[0])
	def xchange(x,y):
	    m = x+1
	    while m<y:
	        result.append(m)
	        m=m+1
	    return y
	reduce(xchange,oldPage)
	list_right = range(1,oldPage[len(oldPage)-1],2733333)
	list_last = result+list_right
	print '加入新添加的页面...%s'%len(list_right)
	print('得到未处理页面%s'%len(list_last))
	print '正在插入数据库...'
	con = db.connect('localhost','root','*******','lagouwang',charset='utf8')
	cur = con.cursor()
	cur.execute("truncate lagouwang.newpages")
	for page in list_last:
		try:
			cur.execute("insert into newpages value(%d)"%page)
		except Exception,e:
			print e
	con.commit()
	cur.close()
	con.close()
	print '将未处理的页面写入数据库完毕.'

if __name__ == '__main__':
	#getClassify()
	#getOtherPages()
	getProxysNumberFromDB()