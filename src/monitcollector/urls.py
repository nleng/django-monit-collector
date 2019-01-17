"""monitcollector URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from monitcollector import views

urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^collector$', views.collector, name='collector'),
    url(r'^server/(?P<server_id>\d+)/$', views.server, name='server'),
    url(r'^server/(?P<server_id>\w+)/process/(?P<process_name>[^/]+)/$', views.process, name='process'),
    url(r'^process_action/(?P<server_id>\d+)/$', views.process_action, name='process_action'),
    url(r'^confirm_delete/(?P<server_id>\d+)/$', views.confirm_delete, name='confirm_delete'),
    url(r'^delete_server/(?P<server_id>\d+)/$', views.delete_server, name='delete_server'),

    url(r'^load_system_data/(?P<server_id>\d+)/$', views.load_system_data, name='load_system_data'),
    url(r'^load_process_data/(?P<server_id>\d+)/(?P<process_name>[^/]+)/$', views.load_process_data, name='load_process_data'),
    url(r'^load_dashboard_table/$', views.load_dashboard_table, name='load_dashboard_table'),
    url(r'^load_system_table/(?P<server_id>\d+)/$', views.load_system_table, name='load_system_table'),
    url(r'^load_process_table/(?P<server_id>\d+)/(?P<process_name>[^/]+)/$', views.load_process_table, name='load_process_table'),
]
