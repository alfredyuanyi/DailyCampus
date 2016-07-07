#coding: utf-8
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from DailyCampus.serializers import *
from MongoDB_Driver import *
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

import redis
import hashlib
import types, math, time
import pymongo
import random, simplejson,json
#发邮件模块
from django.core.mail import send_mail
from smtplib import SMTPException
#根据拿到的mac地址生成经过MD5加密过的字符串，并将这个字符串返回
def TokenWithMD5(mac, userId):
	if type(mac) is types.StringType:
		m = hashlib.md5()
		m.update(mac)
		token = m.hexdigest()
		r = redis.StrictRedis(host=serverip, port = 6379)
		r.set(userId, token)
		return token
		pass
	else:
		return ''
	pass

#根据客户端传过来的ｔｏｋｅｎ，验证是否正确
def IsTokenRight(userId, token):
	r = redis.StrictRedis(host=serverip, port = 6379)
	if r.get(userId) == token:
		return True
		pass
	else:
		return False
	pass
def GetToken(userId):
	r = redis.StrictRedis(host=serverip, port= 6379)
	token = r.get(userId)
	return token
	pass
#使用ｐｙｍｏｎｇｏ从数据库获取所有的集合名，并转换为与２的幂次方对应的键值对集合,
#返回这个集合,注意这个键值对中，键的类型是ｌｏｎｇ
def GetCollectionNames(host = serverip,
	port = 27017,
	database = '南京邮电大学'):
	names = {}
	i = 0
	mongo = MongoDB_Driver(db_ip=host,
		db_port=port,
		database_name=database)
	collectionNames = mongo.db_getCollectionNames()
	for collectionName in collectionNames:
		if collectionName == 'system.indexes':
			continue
			pass
		else:
			key = long(math.pow(2, i))
			names[key] = collectionName
			i = i + 1
		pass
	return names
pass
#从数据库获取所有的部门以及版块信息，返回字典
def GetDepartments(host = serverip,
	port = 27017,
	database = '南京邮电大学',
	collection = 'departments'):
	departments = {}
	i = 10
	mongo = MongoDB_Driver(db_ip=host,
		db_port=port,
		database_name=database)

	dataset = mongo.db_findAll(collection, {})
	for data in dataset:
		departments[str(i)] = data['department']
		key = str(i) + '1'
		departments[key] = data['sectionList']
		i = i + 1
		pass
	return departments
	pass
#向数据库中插入一条用户的关注方向数据，成功返回True，失败返回False
def InsertConcern(host = serverip,
	port = 27017,
	database = '南京邮电大学',
	collection = 'concerns',
	userId = '',
	departments = [],
	sections = {}):
	mongo = MongoDB_Driver(db_ip=host,
		db_port=27017,
		database_name=database)
	dictionary = {'userId': userId, 'departments': departments, 'sections':sections}
	isSecceed = mongo.db_insert(collection, dictionary)
	return isSecceed
	pass
#从数据库获取新闻，并按一定要求排序，返回游标

def GetSortedNews(host = serverip,
	port = 27017,
	database = '南京邮电大学',
	collection = '南京邮电大学教务处',
	condition = {},
	sortcondition = [("timestamp", pymongo.DESCENDING)]):
	mongo = MongoDB_Driver(db_ip=host,
		db_port=port,
		database_name=database)
	curse = mongo.db_findSort(collection = collection,
		condition = condition,
		sortcondition = sortcondition)
	return curse
	pass

#使用pymongo从数据库获取新闻，返回列表，该列表可序列化
def GetNews(host = serverip, port = 27017,
	database = '南京邮电大学',
	collection = '教务处',
	condition = {},
	number = 10):
	mongo = MongoDB_Driver(db_ip = host,
		db_port = port,
		database_name = database)
	#如果打开数据库失败，则直接返回Ｎｏｎｅ
	if not mongo:
		return None
		pass
	else:
		#这个地方如果新闻的数量少于十条会不会有问题还要和小安卓商量一下
		news = mongo.db_findAll(collection,condition)[0:number]
		data = []
		for n in news:
			n['_id'] = str(n['_id'])
			data.append(n)
			pass
		return data
	pass
'''

'''
def Email(email):
	a = random.randint(0, 9)
	b = random.randint(0, 9)
	c = random.randint(0, 9)
	d = random.randint(0, 9)
	e = random.randint(0, 9)
	f = random.randint(0, 9)
	code = str(a) + str(b) + str(c) + str(d) + str(e) + str(f)
	send_mail(
        subject=u"今日校园", message= "[校验码]" + code + "(动态验证码，请勿泄露)，　你正在修改密码，需要进行校验。",
        from_email='b14070316@njupt.edu.cn', recipient_list=[email, ], fail_silently=False,)
	return code
	pass

def EmailCode(email, code):
	send_mail(
        subject=u"今日校园", message= "[校验码]" + code + "(动态验证码，请勿泄露)，　你正在修改密码，需要进行校验。",
        from_email='b14070316@njupt.edu.cn', recipient_list=[email, ], fail_silently=False,)
	return code
	pass
#根据用户关注版块信息，获取对应版块的最新新闻,并返回可序列化的列表
'''
@param host: 数据库ip
@param port: 端口号
@param database: 数据库
@param sections:{
"部门Ａ":{"版块ａ"：timestamp, "版块b": timestamp},
"部门B": {"版块c": timestamp, "版块d": timestamp}
}
@param sortcondition: 排序条件
＠param action: 刷新或加载，'１'表示下拉刷新，'-1'表示加载, '0'表示第一次查询
'''
def GetLastedNews(action,sections,
	host = serverip,
	port = 27017,
	database = '南京邮电大学',
	sortcondition = [("timestamp", pymongo.DESCENDING)]):
	mongo = MongoDB_Driver(db_ip= host,
		db_port= port,
		database_name = database)
	news = []
	if action == '0':
		count = 0
		index = 0
		while 1:
			if count > 10:
				break
				pass
			for depart in sections:
				if count > 10:
					break
					pass
				for section in sections[depart]:
					if count <= 10:
						cursor = mongo.db_findSort(depart,
							sortcondition = sortcondition,
							condition = {'section': section})
						news.append(cursor[index])
						count = count + 1
						pass
					else:
						break
					pass
				pass
			index = index + 1
			pass
		return news
		pass
	for depart in sections:
		for section in sections[depart]:
			if action == '1':
				cursor = mongo.db_findSort(depart,
					sortcondition = sortcondition,
					condition = {"section": section})
				for n in cursor:
					if n['timestamp'] > sections[depart][section]:
						n['_id'] = str(n['_id'])
						news.append(n)
					else:
						break
						pass
					pass
			elif action == '-1':
				cursor = mongo.db_findSort(depart,
					sortcondition = sortcondition,
					condition = {"section": section})
				for n in cursor:
					if n['timestamp'] < sections[depart][section]:
						n['_id'] = str(n['_id'])
						if len(news) >= 10:
							break
							pass
						news.append(n)
					else:
						break
						pass
					pass
			pass
		pass
	return news
	pass
