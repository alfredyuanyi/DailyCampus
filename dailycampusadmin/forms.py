# coding: utf8

from django import forms
from dailycampusadmin.models import *
class AdminUser(forms.Form):
	username = forms.CharField(max_length = 30, required = True, label = '用户名')
	password = forms.CharField(max_length = 25, required = True, label = '密码', widget = forms.PasswordInput)
	def clean_checkusername(self):
		try:
			adminuser = SuperAdmin.objects.get(username = self.cleaned_data['username'])
			pass
		except SuperAdmin.DoesNotExist:
			raise forms.ValidationError('用户名不存在！')
		return adminuser.username
		pass
	def clean_checkpassword(self):
		username = self.clean_data['username']
		pwd = SuperAdmin.objects.get(username = username).pwd
		if pwd != self.clean_data['password']:
			raise forms.ValidationError('密码错误！')
			pass
		return pwd
		pass