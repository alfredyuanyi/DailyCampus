from django.conf.urls import url
from dailycampusadmin import views
urlpatterns = [
 	url(r'^login/$', views.AdminLogin),
 	url(r'^logout/$', views.AdminLogout),
 	# url(r'^createadmin/$', views.CreateAdmin),
 	url(r'adminindex/$', views.AdminIndex),
 	url(r'nupt/collections/$', views.DatabaseCollections),
 	url(r'nupt/collections/seach/$', views.SearchCollections),
 	url(r'nupt/collections/news/seach/(?P<collectionName>.*)/$', views.SearchNews),
 	url(r'adminindex/warehouses/$', views.GetDatabase,{'moduleName': 'warehouses'}),
 	url(r'adminindex/users/$', views.GetDatabase,{'moduleName': 'users'}),
 	url(r'nupt/collections/(?P<collectionName>.*)/$', views.NewsList),

]