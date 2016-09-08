from django.shortcuts import render
from django.http.response import HttpResponse
from background import models
from client_handler import ClientHandler
import json
from django.views.decorators.csrf import csrf_exempt
from utils import redis_tools
from data_handler import DataHandler
from alert_handler import AlertHandler
from utils import mq_tools
from django.core.cache import cache
from monitor.settings import HOST_TIMEOUT_SECOND
import time
from django.shortcuts import render,HttpResponse


REDIS_OBJ = redis_tools.redis_conn()
MQ_CONN = mq_tools.get_mq_conn()

def client_configs(request,client_id):
    if client_id.isdigit():
        client_handler = ClientHandler()
        client_config = client_handler.get_configs(client_id)
        return HttpResponse(json.dumps(client_config))

    else:
        return HttpResponse("client id error")

@csrf_exempt
def service_data_report(request):
    if request.method == "POST":
        client_id = request.POST.get("client_id")
        service_name = request.POST.get("service_name")
        data = request.POST.get("data")
        data = json.loads(data)
        if data['status']!=0:
            return HttpResponse("data error")
        # print client_id,service_name,data
        service = models.Service.objects.get(name=service_name)

        data_handler = DataHandler(client_id,service,data,REDIS_OBJ)
        data_handler.process()

        alert_handler = AlertHandler(client_id,REDIS_OBJ,MQ_CONN)
        alert_handler.process()


    return HttpResponse("service_data_report")

def hosts_status(request):
    return HttpResponse("hosts_status")


def graphs_gerator(request):
    return HttpResponse("graphs_gerator")


def index(request):
    return  render(request,'index.html',{})

def toastr(request):
    return  render(request,'toastr.html',{})

def host_list(request):
    host_list = models.Host.objects.all()
    return  render(request,'host_list.html',{"host_list":host_list})

def host_detail(request,host_id):
    client_handler = ClientHandler()
    client_config = client_handler.get_configs(host_id)
    service_name_list = client_config['services'].keys()
    service_name_dic = {}
    for s in models.Service.objects.filter(name__in=service_name_list):
        service_name_dic[s.name] = {
            'has_sub_service':s.has_sub_service,
        }
        if s.has_sub_service:
            redis_key = 'StatusData_%s_%s_%s' % (host_id,s.name,'latest')
            sub_data = REDIS_OBJ.lrange(redis_key,-1,-1)
            data_point,time_stamp = json.loads(sub_data[0])
            service_name_dic[s.name]['sub_services'] = data_point['data'].keys()




    host_obj = models.Host.objects.get(id=host_id)
    return  render(request,'host_detail.html',{
        "host_obj":host_obj,
        "service_name_dic":service_name_dic
    })



def get_service_item(request):
    if request.method == 'GET':
        service_name = request.GET.get('service_name',None)
        client_id = request.GET.get('client_id',None)
        time_range = request.GET.get('time_range',None)

        service_obj = models.Service.objects.get(name=service_name)
        service_item_list = service_obj.items.select_related().values_list('key',flat=True)
        ret = {
            'has_sub_service' : service_obj.has_sub_service,
            'service_item_list':list(service_item_list)
        }
        if service_obj.has_sub_service:
            redis_key = 'StatusData_%s_%s_%s' % (client_id,service_name,'latest')
            sub_data = REDIS_OBJ.lrange(redis_key,-1,-1)
            data_point,time_stamp = json.loads(sub_data[0])
            ret['sub_services'] = data_point['data'].keys()

        return HttpResponse(json.dumps(ret))


def get_realtime_data(request):
    if request.method == 'GET':
        client_id = request.GET.get('client_id',None)
        service_name = request.GET.get('service_name',None)
        key = request.GET.get('key',None)
        sub_key = request.GET.get('sub_key',None)
        redis_key = 'StatusData_%s_%s_%s' % (client_id,service_name,'latest')
        data_point = REDIS_OBJ.lrange(redis_key,-1,-1)
        data , time_stamp = json.loads(data_point[0])
        if data:
            if data.has_key("data"):
                return HttpResponse(json.dumps([int(time_stamp*1000),float(data["data"][sub_key][key])]))
            else:
                return HttpResponse(json.dumps([int(time_stamp*1000),float(data[key])]))


def get_service_item_data(request):
    if request.method == 'GET':
        time_range = request.GET.get('time_range','latest')
        client_id = request.GET.get('client_id',None)
        service_name = request.GET.get('service_name',None)
        service_obj = models.Service.objects.get(name=service_name)
        key = request.GET.get('key',None)

        if time_range == 'realtime':
            redis_key = 'StatusData_%s_%s_%s' % (client_id,service_name,'latest')
        else:
            redis_key = 'StatusData_%s_%s_%s' % (client_id,service_name,time_range)

        data_list = REDIS_OBJ.lrange(redis_key,0,-1)

        if service_obj.has_sub_service:
            ret = []
            sub_key = request.GET.get('sub_key',None)
            for p in data_list:
                data_point,time_stamp = json.loads(p)
                if not data_point: continue
                if time_range == 'latest' or time_range == 'realtime':
                    if data_point['data']:
                        ret.append([int(time_stamp*1000),round(float(data_point['data'][sub_key][key]),2)])
                else:
                    if data_point['data'].has_key(sub_key):
                        ret.append([int(time_stamp*1000),round(float(data_point['data'][sub_key][key][0]),2)])
            return HttpResponse(json.dumps(ret))
        item_list = []
        for p in data_list:
            data , time_stamp =json.loads(p)
            if not data: continue
            if time_range == 'latest'or time_range == 'realtime':
                item_list.append([int(time_stamp*1000),round(float(data[key]),2)])
            else:
                item_list.append([int(time_stamp*1000),round(float(data[key][0]),2)])
        return HttpResponse(json.dumps(item_list))


def get_host_alive_status(request):
    if request.method == 'GET':
        host_alive_list = models.Host.objects.all()
        ret = {}
        for h in host_alive_list:
            ret[h.id]=[h.status,h.get_status_display(),h.name,h.ip_addr]
        return HttpResponse(json.dumps(ret))