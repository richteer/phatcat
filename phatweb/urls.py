from django.conf.urls import url, include 
import phatweb.views as views

urlpatterns = [
	url(r'^$', views.root),
	url(r'^cat/$', views.cat),
	url(r'^cat/(?P<id>\d+)/?$', views.cat_detail),
]
