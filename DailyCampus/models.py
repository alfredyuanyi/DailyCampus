#coding: utf-8
from __future__ import unicode_literals

from django.db import models
from mongoengine import *
# Create your models here.
serverip = '180.209.64.38'
connect('南京邮电大学', host = serverip, port = 27017)
#用户类
class User(Document):
	userId = StringField(required = True)
	pwd = StringField(required = True)
	email = StringField(required = True)
	tel = StringField(required = True)
	school = StringField(required = True)
	token = StringField(required = False, default = '')
	def __unicode__(self):
		return self.userId
		pass
#关注方向类
#userId:用户名，与用户表建立逻辑关系
#departments:用户关注的部门
#sections:用户具体关注的部门版块
#departments的类型为列表，eg: ["部门Ａ", "部门Ｂ"]
#sections的类型为字典，键为部门名称，值为字典（该字典的值为板块名称，值为衡量该新闻是否为最新新闻的ｘ值）
#sections的例子，eg: {
#	"": {"": , "": },
#	"": {"": , "": }}
class Concerns(Document):
	userId = StringField(required = True)
	departments = ListField(required = True, default = [])
	sections = DictField(required = True, default = {})
	def __unicode__(self):
		return self.userId + 'Concerns'
		pass
#新闻通知类
#timestamp:衡量是否为最新的新闻的量，值类型为int
#date:新闻的时间
#section:新闻所属的板块
#depart:新闻所属的部门
#title:新闻的标题
#url:新闻的超链接
class DepartmentNames(Document):
	title = StringField()
	url = StringField()
	timestamp = IntField()
	date = StringField()
	section = StringField()
	depart = StringField()
	# clickRate = IntField(default = 0)
	def __unicode__(self):
		return self.depart
		pass
#部门及版块类
#depart:部门或机构
#sectionList:　该部门下的版块
#eg:["版块Ａ", "版块Ｂ", "版块Ｃ"]
class DepartmentAndSection(Document):
	depart = StringField()
	sectionList = ListField()

#用户修改密码验证类
class Password(Document):
	userId = StringField()
	authCode = StringField()
	isRight = BooleanField()
	createTime = FloatField()




