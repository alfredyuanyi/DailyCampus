# coding: utf8
from __future__ import unicode_literals


from mongoengine import *
from dailycampus.settings import serverip, dbport
# Create your models here.
connect('南京邮电大学', host = serverip, port = dbport)

#管理员类
class SuperAdmin(Document):
	username = StringField(required=True)
	pwd = StringField(required=True)
	email = EmailField(required=True)
	isLogin = BooleanField(default=False)
	