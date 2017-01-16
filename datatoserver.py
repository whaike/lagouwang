#/usr/bin/python
#-*-coding:utf-8 -*-

#csv to mysql
import pandas as pd
import MySQLdb as db

df = pd.read_csv('lagouwang.csv',sep=';',encoding="utf-8",na_values='others')
print 'df is OK'
df.fillna('others')
con = db.connect('localhost','root','******','lagouwang',charset='utf8')
cur = con.cursor()
print 'cur is OK'
df1 = df.fillna('others')
lines = 0
def input(x):
    global lines
    sql = "insert into lagouwang.lagou(publish_time,title,jobkwd,salary,background,industry,company,classf) values(%s,%s,%s,%s,%s,%s,%s,%s)"
    val = (x['publish_time'],x['title'],x['jobkwd'],x['salary'],x['background'],x['industry'],x['company'],x['classf'])
    cur.execute(sql,val)
    lines = lines +1
    if lines % 10000 == 0:
        print 'had insert: %d'%lines
        con.commit()
df1.apply(input,axis=1)
con.commit()
cur.close()
con.close()