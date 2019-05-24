from django.contrib import admin
from django.urls import path, re_path

from . import views

urlpatterns = [
	path('', views.index, name = 'index'),
    path('start_list/', views.start_list, name = 'start_list'),
    re_path(r'^start_list/(\d+)/(\d+)/(\d+)$', views.start_protocol, name = 'start_list'), 
	path('result_list/', views.result_list, name = 'result_list'),
	re_path(r'^result_list/(\d+)/(\d+)/(\d+)$', views.result_protocol, name = 'result_list'),
]
