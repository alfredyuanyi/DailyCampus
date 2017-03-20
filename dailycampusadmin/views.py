# coding: utf8

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from DailyCampus.MongoDB_Driver import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth import authenticate, logout,login
from django.http import Http404
from DailyCampus.helpfunctions import *
from dailycampus.settings import serverip, dbport
from models import SuperAdmin
from forms import AdminUser
import base64
# Create your views here.

def AdminLogin(request):
	if request.method == 'GET':
		return render(request, template_name = 'login.html')
		pass
	if request.method == 'POST':
		form = AdminUser(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			request.session['username'] = data['username'] 
			try:
				adminuser = SuperAdmin.objects.get(username = data['username'])
				pass
			except SuperAdmin.DoesNotExist:
				return HttpResponse('账号密码错误！')
			adminuser.save()
			return render(request, 
				template_name = 'adminindex.html',
				context = {'user': adminuser, 'haslogin': True})
			pass
		else:
			return HttpResponse('未知的错误！')
		pass
	pass

def CheckLogin(request):
	result = {}
	if 'username' in request.session:
		try:
			user = SuperAdmin.objects.get(username = request.session['username'])
			pass
		except SuperAdmin.DoesNotExist:
			result = {'user': None, 'islogin': False}
			return result
		result = {'user': user, 'islogin': True}
		return result
	else:
		result = {'user': None, 'islogin': False}
		return result
	pass
def CheckRequestMethodIsGET(request):
	if request.method != 'GET':
		return False
	else:
		return True
	pass
def AdminIndex(request):
	if CheckRequestMethodIsGET(request):
		result = CheckLogin(request)
		if result['islogin']:
			return render(request, 
				template_name = 'adminindex.html',
				context = {'user': result['user'], 'haslogin': True})
			pass
		else:
			return HttpResponse('您还未登录，请重新登陆！')
		pass
	else:
		return Http404
	pass
def DatabaseCollections(request):
	if CheckRequestMethodIsGET(request):
		result = CheckLogin(request)
		if result['islogin']:
			#返回所有该数据库的集合
			mongo = MongoDB_Driver(db_ip='180.209.64.38',
				db_port=40020,
				database_name='南京邮电大学'.decode('utf8'))
			collectionNames = mongo.db_getCollectionNames()
			encodeCollectionNames = {}
			for name in collectionNames:
				encodeCollectionNames[name] = base64.b64encode(name.encode('utf8'))
				pass
			
			return render(request, 
				template_name = 'collections.html',
				context = {'collectionDicts': encodeCollectionNames, 'user': result['user'], 'haslogin': True})
			pass
		else:
			return HttpResponse('您还未登录，请重新登陆！')
		pass
	else:
		return HttpResponse('错误的请求方式！')
	pass
def SearchCollections(request):
	if CheckRequestMethodIsGET(request):
		result = CheckLogin(request)
		if result['islogin']:
			collectionName = request.GET['collectionName']
			mongo = MongoDB_Driver(db_ip='180.209.64.38',
				db_port=40020,
				database_name='南京邮电大学'.decode('utf8'))
			collectionNames = mongo.db_getCollectionNames()
			searchResult = {}
			for name in collectionNames:
				if name.find(collectionName) != -1:
					searchResult[name] = base64.b64encode(name.encode('utf8'))
					pass
				pass
			return render(request, 
				template_name = 'collections.html',
				context = {'collectionDicts': searchResult, 'user': result['user'], 'haslogin': True})
			pass
		else:
			return HttpResponse('您还未登录，请重新登陆！')
		pass
	else:
		return HttpResponse('错误的请求方式！')
	pass
def NewsList(request, collectionName):
	if CheckRequestMethodIsGET(request):
		result = CheckLogin(request)
		if result['islogin']:
			name = base64.b64decode(collectionName)
			mongo = MongoDB_Driver(db_ip='180.209.64.38',
				db_port=40020,
				database_name='南京邮电大学'.decode('utf8'))
			newsList = mongo.db_findSort(collection = name.decode('utf8'), condition = {}, sortcondition = [("date", pymongo.DESCENDING)])
			return render(request,
				template_name = 'news.html',
				context = {'newsList': newsList, 'user': result['user'], 'haslogin': True,'collection': name, 'decodeCollectionName': collectionName})
			pass
		else:
			return HttpResponse('您还未登录，请重新登陆！')
		pass
	else:
		return HttpResponse('错误的请求方式！')
	pass
def GetDatabase(request, moduleName):
	if CheckRequestMethodIsGET(request):
		result = CheckLogin(request)
		if result['islogin']:
			if moduleName == 'warehouses':
				return render(request,
					template_name = 'warehouse.html',
					context = {'user': result['user'], 'haslogin': True})				
				pass
			elif moduleName == 'users':
				return render(request,
					template_name = 'user.html',
					context = {'user': result['user'], 'haslogin': True})
			else:
				return HttpResponse('参数错误！')
			pass
		else:
			return HttpResponse('您还未登录，请重新登陆！')
		pass
	else:
		return HttpResponse('错误的请求方式！')
	pass
def SearchNews(request, collectionName):
	if CheckRequestMethodIsGET(request):
		result = CheckLogin(request)
		if result['islogin']:
			name = base64.b64decode(collectionName)
			mongo = MongoDB_Driver(db_ip='180.209.64.38',
				db_port=40020,
				database_name='南京邮电大学'.decode('utf8'))
			newsList = mongo.db_findSort(collection = name.decode('utf8'), condition = {}, sortcondition = [("date", pymongo.DESCENDING)])
			searchResult = []
			for news in newsList:
				if news['title'].find(request.GET['keywords']) != -1:
					searchResult.append(news)
					pass
				pass
			return render(request,
				template_name = 'news.html',
				context = {'newsList': searchResult, 'user': result['user'], 'haslogin': True, 'collection': name, 'decodeCollectionName': collectionName})
			pass
		else:
			return HttpResponse('您还未登录，请重新登陆！')
		pass
	else:
		return HttpResponse('错误的请求方式！')
	pass

def AdminLogout(request):
	if CheckRequestMethodIsGET(request):
		result = CheckLogin(request)
		if result['islogin']:
			del request.session['username']
			result['user'].islogin = False
			result['user'].save()
			return redirect('/admin/login/')
			pass
		else:
			return HttpResponse('您还未登录，请重新登陆！')
		pass
	else:
		return HttpResponse('错误的请求方式！')
	pass