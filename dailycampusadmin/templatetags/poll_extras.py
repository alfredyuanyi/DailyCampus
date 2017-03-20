# coding:utf8
from django import template
#自定义过滤器
register = template.Library()
@register.filter(name = 'dictValue')
def GetDictValue(value, dictionary):
	return dictionary[value]
	pass