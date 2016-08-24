__author__ = 'zhaobin022'
#_*_coding:utf-8_*_


configs ={
    'HostID': 1,
    "Server": "192.168.26.67",
    "ServerPort": 8080,
    "urls":{

        'get_configs' :['api/client/config','get'],  #acquire all the services will be monitored
        'service_report': ['api/client/service/report/','post'],

    },
    'RequestTimeout':30,
    'ConfigUpdateInterval': 10, #5 mins as default

}