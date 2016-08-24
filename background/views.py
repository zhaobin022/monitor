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

