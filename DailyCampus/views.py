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
from helpfunctions import *
import redis
import hashlib
import types, math, time
import pymongo
import random, simplejson,json
#发邮件模块
from django.core.mail import send_mail
from smtplib import SMTPException
from dailycampus.settings import serverip, dbport
# Create your views here.


class JsonResponse(HttpResponse):
	def __init__(self, data, **kwargs):
		content = JSONRenderer().render(data)
		kwargs['content_type'] = 'application/json'
		super(JsonResponse, self).__init__(content,**kwargs)
		pass

#以下皆为核心ａｐｉ

class Users(APIView):
	# @csrf_exempt
	'''
	@function:　新建一条用户记录
	@param:　新的用户记录
	'''
	def post(self, request, format = None):
		serializer = UserSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			department = Department()
			return Response(department.data, status = 201)
			pass
		return Response(serializer.errors, status = 400)
		pass
	def get(self, requst, format = None):
		users = User.objects.all()
		serializer = UserSerializer(users, many = True)
		return JsonResponse(serializer.data, status = 201)
		pass
	'''
	@function:　更新一条用户记录
	@param: 新的用户记录
	@return: 已更新的用户记录
	'''
	def put(self, request, format = None):
		requestData = JSONParser().parse(request)
		token = requestData['token']
		user = User.objects.get(token = token)
		serializer = UserSerializer(user, data = requestData)
		if serializer.is_valid():
			serializer.save()
			return JsonResponse(serializer.data, status = 201)
			pass
		return JsonResponse(requestData, status = 400)
		pass
	pass
#处理和通知公告有关的事物
'''
@function :下拉刷新或者加载
@param userId:用户名
@param token:令牌
@param action: １表示下拉刷新，-1表示加载
@param school: 学校
@param depart: 欲刷新或加载的部门，参数形如,
	{"部门名称": {"版块ａ": timestamp, "版块ｂ"：　timestamp}}
'''
@csrf_exempt
def News(request):
	requestData = JSONParser().parse(request)
	userId = requestData['userId']
	token = requestData['token']
	#token验证
	if IsTokenRight(userId, token):

		if request.method == 'POST':
			#action，　１表示下拉刷新，-1表示加载
			action = requestData['action']
			d = requestData['depart']
			print d 
			user = User.objects.filter(userId = userId)
			if user.count() < 1 or user.count() > 1:
				requestData['error'] = '用户名不存在或者存在多个该用户'.decode('utf-8')
				return JsonResponse(requestData, status = 400)
				pass
			else:
				school = user[0]['school']
			depart = requestData['depart']
			if action == '1':
				sortcondition = [('timestamp', pymongo.DESCENDING)]
				news = GetLastedNews(host = serverip,
					port=dbport,
					database=school,
					sections=depart,
					sortcondition=sortcondition,
					action=action)
				return JsonResponse(news, status = 201)
				pass
			elif action == '-1':
				sortcondition = [('timestamp', pymongo.ASCENDING)]
				news = GetLastedNews(host=serverip,
					port=dbport,
					database=school,
					sections=depart,
					sortcondition=sortcondition,
					action=action)
				return JsonResponse(news, status = 201)
				pass
			elif action == '0':
				sortcondition = [('timestamp', pymongo.DESCENDING)]
				news = GetLastedNews(host=serverip,
					port=dbport,
					database=school,
					sections = depart,
					sortcondition = sortcondition,
					action = action
					)
				return JsonResponse(news, status = 201)
				pass
			else:
				requestData['error'] = '非法的操作'.decode('utf-8')
				return JsonResponse(requestData, status = 400)
			pass
		requestData['error'] = '非法的http方法'.decode('utf-8')

		return JsonResponse(requestData, status = 400)
	requestData['error'] = 'token错误'.decode('utf-8')
	return JsonResponse(requestData, status = 401)
	pass
@csrf_exempt
def register(request):
	if request.method == 'POST':
		data = JSONParser().parse(request)
		if User.objects.filter(userId = data["userId"]).count() >0:
			return JsonResponse(data, status = 400)
		mac = str(data['mac'])
		userId = data['userId']
		token = TokenWithMD5(mac, userId)
		data['token'] = token
		school = data['school']
		serializer = UserSerializer(data = data)
		if serializer.is_valid():
			#获取所有的部门及其版块
			departments = GetDepartments(host=serverip,
				port=dbport,
				database=school,
				collection='departments')
			# collectionnames = GetCollectionNames(host=serverip,
			# 	port=dbport,
			# 	database=school)
			serializer.save()
			department = dict(departments, **serializer.data)
			department['token'] = token
			return JsonResponse(department, status = 201)
			pass
		return JsonResponse(serializer.errors, status = 400)
	elif request.method == 'GET':
		users = User.objects.all()
		serializer = UserSerializer(users, many = True)
		return JsonResponse(serializer.data, status = 201)
	elif request.method == 'PUT':
		requestData = JSONParser().parse(request)
		userId = requestData['userId']
		token = requestData['token']
		if IsTokenRight(userId = userId, token = token):
			user = User.objects.filter(userId = userId)
			user[0].modify(userId = userId,
				school = requestData['school'],
				tel = requestData['tel'],
				email = requestData['email'])
			user[0].save()
			userConcern = Concerns.objects.filter(userId = userId)
			userConcern[0].modify(userId = userId)
			userConcern[0].save()
			userpwd = Password.objects.filter(userId = userId)
			userpwd[0].modify(userId = userId)
			userpwd[0].save()
			return HttpResponse([requestData], status = 201)
			pass
	return JsonResponse(serializer.errors, status = 400)
	pass

@csrf_exempt
def login(request):
	data = JSONParser().parse(request)
	userId = data['userId']
	if request.method == 'POST':
		user = User.objects.filter(userId = data['userId'])
		if user.count() < 1:
			return JsonResponse(data, status = 400)
			pass
		elif user[0].pwd == data['pwd']:
			#这里应该是账号密码都正确,返回新闻
			# school = user[0].school
			# mongo = MongoDB_Driver(db_ip=serverip,
			# 	db_port=dbport,
			# 	database_name = school,)
			# userConcern = mongo.db_findOne(collection = 'testconcerns',
			# 	condition = {'userId': userId})
			# sections = userConcern['sections']
			# news = GetLastedNews(host=serverip,
			# 	port=dbport,
			# 	database=school,
			# 	sections = sections,
			# 	sortcondition=[("timestamp", pymongo.DESCENDING)],
			# 	action = '1')
			news = GetNews(host=serverip,
				port=dbport,
				database='南京邮电大学'.decode('utf-8'),
				collection='| Nanjing University of Posts and Telecommunications'.decode('utf-8'),
				condition={'section': '南邮要闻'.decode('utf-8')},
				number=10)
			token = GetToken(userId)
			news.append({'token': token})
			return JsonResponse(news, status = 201)
		else:
			#这里应该是存在这个账号，但是密码不正确，重新登陆
			return JsonResponse(data, status = 401)
		pass
	return JsonResponse(data, status = 403)
	pass

@csrf_exempt
def Concerns(request):
	data = JSONParser().parse(request)
	#没有做唯一性处理
	'''
	@function 新建一条用户关注记录
	@param 
	@return
	'''
	if request.method == 'POST':
		userId = data['userId']
		token = data['token']
		if User.objects.filter(userId = userId).count() > 1 or User.objects.filter(userId = userId).count < 1:
			return JsonResponse(data, status = 400)
			pass
		else:
			if IsTokenRight(userId, token):
				#departments为列表，形如["部门Ａ","部门Ｂ"]
				departments = data['departments']
				#sections为字典，键为部门名称，值为列表（存储该部门下，此用户关注的板块名称），
				#形如{"部门Ａ"：["版块Ａ","版块Ｂ"]}
				sections = data['sections']
				school = data['school']
				# concerns = {}
				# concernedSections = {}
				# concernedNews = []
				# for depart in sections:
				# 	for section in sections[depart]:
				# 		sortcondition = [("timestamp", pymongo.DESCENDING)]
				# 		cursor = GetSortedNews(host=serverip,
				# 			port=dbport,
				# 			database=school,
				# 			collection=depart,
				# 			condition={'section': section},
				# 			sortcondition = sortcondition)
				# 		if cursor == None:
				# 			return JsonResponse(data, status = 404)
				# 			pass
				# 		else:
				# 			news = cursor[0]
				# 			timestamp = news['timestamp']
				# 			news['_id'] = str(news['_id'])
				# 			concernedNews.append(news)
				# 			concernedSections[section] = timestamp
				# 		pass
				# 	concerns[depart] = concernedSections
				# 	concernedSections = {}
				# 	pass
				news = GetNews(host=serverip,
					port=dbport,
					database='南京邮电大学'.decode('utf-8'),
					collection='南京邮电大学| Nanjing University of Posts and Telecommunications'.decode('utf-8'),
					condition={'section': '南邮要闻'.decode('utf-8')},
					number=10)
				if Concerns.objects.filter(userId = userId).count > 0:
					return HttpResponse([requestData,{'error': 'this userConcern has existed'}], status = 400)
					pass
				isSecceed = InsertConcern(host=serverip,
					port=dbport,
					database=school,
					collection='testconcerns',
					userId=userId,
					departments=departments,
					sections = sections
					)
				if isSecceed:
					return JsonResponse(news, status = 201)
					pass
				else:
					return JsonResponse(data, status = 400)
					pass
				pass
			else:
				return JsonResponse(data, status = 401)
		pass
	'''
	@function　修改一条用户关注记录,还没有写完
	@param 
	@return
	'''
	if request.method == 'PUT':
		requestData = JSONParser().parse(request)
		userId = requestData['userId']
		token = requestData['token']
		if IsTokenRight(userId = userId, token = token):
			departments = requestData['departments']
			sections = requestData['sections']
			userConcern = Concerns.objects.filter(userId = userId)
			if userConcern and userConcern.count == 1:
				userConcern[0][departments] = departments
				userConcern[0][sections] = sections
				userConcern[0].save()
				return HttpResponse([requestData], status = 201)
				pass
			return HttpResponse([requestData, {'error': 'such userConcern not exist or has more than two records'}], status = 400)
			pass
		return HttpResponse([requestData, {'error':'wrong token'}], status = 401)
	return JsonResponse(data, status = 403)
	pass

@csrf_exempt
def Departments(request):
	
	pass
'''
@function: 发送验证码到邮箱
@param userId:用户名
@param token: 令牌
@param email:邮箱
'''
@csrf_exempt
def sendEmail(request):
	if request.method == 'POST':	
		data = JSONParser().parse(request)
		userId = str(data['userId'])
		token = data['token']
		if IsTokenRight(userId = userId, token = token):
			user = User.objects.filter(userId = userId)
			change = Password.objects.filter(userId = userId)
			email = data['email']
			if change and user:
				if int(time.time() - float(change[0]['createTime'])) <= 1800:
					code = EmailCode(email, change[0]['authCode'])
					change[0].modify(isRight = False)
					change[0].save()
					data['code'] = code
					return HttpResponse([data], status = 201)
					pass
				else:				
					code = Email(email)
					change[0].modify(authCode = code, isRight = False, createTime = time.time())
					change[0].save()
					data['code'] = code
					return HttpResponse([data], status = 201)
				pass
			else:
				code = Email(email)
				data['code'] = code
				pwd = Password(userId = userId, authCode = code, isRight = False, createTime = time.time())
				pwd.save()
				return HttpResponse([data], status = 201)		
			pass
		return HttpResponse(data, status = 400)
	return HttpResponse([{'error':'refuse asshole request'}], status =400)
	pass
'''
@function: 确认验证码是否正确
@param userId:　用户名
@param token:　令牌
@param authCode:　验证码
@param newpwd:　新密码
'''
@csrf_exempt
def checkAuthCode(request):
	if request.method == 'POST':
		requestData = JSONParser().parse(request)
		userId = requestData['userId']
		token = requestData['token']
		if IsTokenRight(userId = userId, token = token):
			change = Password.objects.filter(userId = userId)
			user = User.objects.filter(userId = userId)
			if change and change[0]['authCode'] == requestData['authCode'] and user and int(time.time() - change[0]['createTime']) <= 1800:
				changingUser = user[0]
				changingUser.modify(pwd = requestData['newpwd'])
				changingUser.save()
				change[0].delete()
				change[0].save()
				return HttpResponse([requestData], status = 201)
				pass
			elif int(time.time() - float(change[0]['createTime'])) > 1800:
				change[0].delete()
				change[0].save()
				return HttpResponse([requestData], status = 400)
			return HttpResponse([requestData], status = 400)
			pass
		return HttpResponse([requestData], status = 401)
		pass
	return HttpResponse([JSONParser().parse(request)], status = 400)
	pass

@csrf_exempt
def modifyConcerns(request):
	if request.method == 'POST':
		requestData = JSONParser().parse(request)
		userId = requestData['userId']
		token = requestData['token']
		if IsTokenRight(userId = userId,  token = token):
			school = requestData['school']
			mongo = MongoDB_Driver(db_ip=serverip,
				db_port= dbport,
				database_name = '南京邮电大学')
			userConcerns = mongo.db_findAll('concerns', {'userId': userId})[0]['sections']
			allConcerns = GetDepartments(host=serverip,
						port=dbport,
						database=school,
						collection='departments')
			return HttpResponse([userConcerns,allConcerns], status = 201)
			pass
		else:
			return HttpResponse([requestData,{'error': 'wrong token'}], status = 401)
		pass
	return HttpResponse([JSONParser().parse(request), {"error": "wrong request function"}])
	
	pass


