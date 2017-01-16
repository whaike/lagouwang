#-*-coding:utf-8 -*-
from django.db import models


class Lagou(models.Model):
    publish_time = models.DateField(blank=True, null=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    jobkwd = models.CharField(max_length=500, blank=True, null=True)
    salary = models.CharField(max_length=500, blank=True, null=True)
    background = models.CharField(max_length=500, blank=True, null=True)
    company = models.CharField(max_length=500, blank=True, null=True)
    industry = models.CharField(max_length=500, blank=True, null=True)
    companyurl = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    pages = models.IntegerField(unique=True)
    classf = models.CharField(max_length=500, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lagou'


class Newpages(models.Model):
    newp = models.IntegerField(unique=True)

    class Meta:
        managed = False
        db_table = 'newpages'


class Svgdatas(models.Model):
    name = models.CharField(primary_key=True, max_length=100)
    data = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'svgdatas'


class Xiciproxy(models.Model):
    ip = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'xiciproxy'
