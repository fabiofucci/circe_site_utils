from django.urls import path

from . import views

urlpatterns = [
    path('request_demo', views.request_demo, name='request_demo'),
    path('request_buy', views.request_buy, name='request_buy'),
    path('request_info', views.request_info, name='request_info')
]