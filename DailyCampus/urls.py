from django.conf.urls import url
from DailyCampus import views
urlpatterns = [
	url(r'^api/v1/newusers/$', views.register),
	url(r'^api/v1/users/login/$', views.login),
	url(r'^api/v1/concerns/newconcerns/$', views.Concerns),
	url(r'^api/v1/users/lists/$', views.Users.as_view()),
	url(r'^api/v1/news/$', views.News),
	url(r'^api/v1/users/pwd/email/code/', views.sendEmail),
	url(r'^api/v1/users/pwd/newpwd/', views.checkAuthCode),
	url(r'^api/v1/users/concerns/all/', views.modifyConcerns),
]