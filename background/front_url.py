__author__ = 'zhaobin022'
from django.conf.urls import url

import views
urlpatterns = [
    url(r'host_list/$',views.host_list,name='host_list' ),
    url(r'^host_detail/([0-9]+)/$', views.host_detail, name='host_detail'),
]