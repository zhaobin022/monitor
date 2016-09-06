__author__ = 'zhaobin022'
from django.conf.urls import url

import views
urlpatterns = [
    url(r'client/config/(\d+)/$',views.client_configs ),
    url(r'client/service/report/$',views.service_data_report ),
    url(r'hosts/status/$',views.hosts_status,name='get_hosts_status' ),
    url(r'graphs/$',views.graphs_gerator,name='get_graphs' ),
    url(r'get_service_item/$',views.get_service_item,name='get_service_item' ),
    url(r'get_service_item_data/$',views.get_service_item_data,name='get_service_item_data' ),
    url(r'get_realtime_data/$',views.get_realtime_data,name='get_realtime_data' ),
    url(r'get_host_alive_status/$',views.get_host_alive_status,name='get_host_alive_status' ),
]