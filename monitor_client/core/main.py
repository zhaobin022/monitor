__author__ = 'zhaobin022'

from conf import settings
import time
import requests
import urlparse
import threading
from plugins import plugin_api
import json
import sys

class ClientHandler(object):
    def __init__(self):
        self.monitor_services = {}
        self.host = 'http://%s:%d' % (settings.configs['Server'],settings.configs['ServerPort'])


    def url_request(self,request_url,request_type,result_type,content=None):
        if request_type == 'get':
            r = requests.get(request_url)
            return r.json()
        elif request_type == 'post':
            r = requests.post(request_url, data=content)
            # print r.status_code
            if r.status_code != 200:
                with open('error.html','w') as f:
                    f.write(r.text)
            return r.text
    def load_config(self):

        request_uri = settings.configs['urls']['get_configs'][0]
        client_id = settings.configs['HostID']
        request_type = settings.configs['urls']['get_configs'][1]

        request_url = urlparse.urljoin(
            self.host,
            request_uri,
        )
        request_url = request_url+'/%d' % client_id

        ret = self.url_request(request_url,request_type,'json')
        # data example: {u'services': {u'LinuxCpu': [u'get_linux_cpu', 60], u'LinuxMemory': [u'get_memory_info', 60], u'LinuxNetwork': [u'GetNetworkStatus', 10]}}
        service_name_ret_from_server = set(ret['services'].keys())
        service_name_ret_from_local = set(self.monitor_services.keys())

        need_remove_set = service_name_ret_from_local - service_name_ret_from_server
        need_add_set = service_name_ret_from_server - service_name_ret_from_local
        need_update_set = service_name_ret_from_server & service_name_ret_from_local
        for i in need_remove_set:
            del self.monitor_services[i]

        for i in need_add_set:
            self.monitor_services[i] = ret['services'][i]

        for i in need_update_set:
            if self.monitor_services[i][0] != ret['services'][i][0]:
                self.monitor_services[i][0] = ret['services'][i][0]

            if self.monitor_services[i][1] != ret['services'][i][1]:
                self.monitor_services[i][1] = ret['services'][i][1]
        print self.monitor_services
    def invoke_plugin_and_send_monitor_data(self,service_name,plugin_name):
        if hasattr(plugin_api,plugin_name):
            f = getattr(plugin_api,plugin_name)
            plugin_callback = f()
            report_data = {
                'client_id':settings.configs['HostID'],
                'service_name':service_name,
                'data':json.dumps(plugin_callback)
            }
            request_uri = settings.configs['urls']['service_report'][0]
            request_type = settings.configs['urls']['service_report'][1]

            request_url = urlparse.urljoin(
                self.host,
                request_uri,
            )
            print report_data

            ret = self.url_request(request_url,request_type,'json',content=report_data)
            # print ret
    def handler(self):
        exit_flag = False
        last_config_update_time = 0

        while not exit_flag:
            try:
                if time.time() - last_config_update_time > settings.configs['ConfigUpdateInterval']:
                    last_config_update_time = time.time()
                    self.load_config()

                for service_name,arg_list in self.monitor_services.items():
                    plugin_name = arg_list[0]
                    interval = arg_list[1]
                    if len(arg_list) == 2:
                        arg_list.append(time.time())
                        t = threading.Thread(target=self.invoke_plugin_and_send_monitor_data,args=(service_name,plugin_name))
                        t.start()

                    else:
                        last_update_time = arg_list[2]
                        if time.time() - last_update_time > interval:
                            arg_list[2] = time.time()
                            t = threading.Thread(target=self.invoke_plugin_and_send_monitor_data,args=(service_name,plugin_name))
                            t.start()
                time.sleep(1)
            except KeyboardInterrupt:
                sys.exit("normal quit")
