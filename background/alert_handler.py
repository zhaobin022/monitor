__author__ = 'zhaobin022'
from background import models
import json
import copy
import time
import operator

class AlertHandler(object):
    def __init__(self,client_id,redis_obj,mq_conn):
        self.client_id = client_id
        self.redis_obj = redis_obj
        self.mq_conn = mq_conn
        self.mq_channel = self.mq_conn.channel()


    def get_host_triggers(self):
        triggers = []
        host_obj = models.Host.objects.get(id=self.client_id)
        for t in host_obj.templates.select_related():
            triggers.extend(t.triggers.select_related())

        for g in host_obj.host_groups.select_related():
            for t in g.templates.select_related():
                triggers.extend(t.triggers.select_related())
        return set(triggers)

    def load_data_from_redis(self,time_in_second,interval,redis_key):
        data_point_count = time_in_second/interval+5
        redis_slice = self.redis_obj.lrange(redis_key,-data_point_count,-1)
        ret = []
        redis_slice.reverse()
        for p in redis_slice:
            p = json.loads(p)
            update_time = p[1]
            if time.time() - update_time < time_in_second:
                ret.append(p)
        return ret

    def deal_expression(self,expression):
        time_range = expression.data_calc_args.split(',')[0]
        time_in_second = int(time_range) * 60
        interval = expression.service.interval
        redis_key = "StatusData_%s_%s_latest" %(self.client_id,expression.service.name)

        data_set = self.load_data_from_redis(time_in_second,interval,redis_key)

        data_calc_func = getattr(self,'get_%s' % expression.data_calc_func)
        ret = data_calc_func(data_set,expression)
        return ret

    def get_avg(self,data_set,expression):
        temp_dic = {}

        if data_set:
            data_point = data_set[0]
            if 'data' not in data_point[0].keys():
                ret_list = []
                for p in data_set:
                    val = p[0][expression.service_index.key]
                    ret_list.append(float(val))

                avg_num = sum(ret_list)/len(ret_list)
                f = getattr(operator,expression.operator_type)
                ret = [f(avg_num,expression.threshold),round(float(avg_num),2),None]
                return ret
            else:
                ret_dic = {}
                for key,val in data_point[0]['data'].items():
                    if  key == expression.specified_index_key:
                        for sub_key , sub_val in val.items():
                            if sub_key == expression.service_index.key:
                                if not ret_dic.has_key(key):
                                    ret_dic[key] = {}
                                if not ret_dic[key].has_key(sub_key):
                                    ret_dic[key][sub_key] = []


                for p in data_set:
                    data_point,time_stamp = p
                    for key , val in data_point['data'].items():
                        if  key == expression.specified_index_key:
                            for sub_key , sub_val in val.items():
                                if sub_key == expression.service_index.key:
                                    ret_dic[key][sub_key].append(float(sub_val))
                avg_num = sum(ret_dic[expression.specified_index_key][expression.service_index.key])/len(ret_dic[expression.specified_index_key][expression.service_index.key])
                if hasattr(operator,expression.operator_type):
                    func = getattr(operator,expression.operator_type)
                    status =  func(avg_num,expression.threshold)
                    return [status,round(avg_num,2),expression.specified_index_key]


    def process(self):
        triggers = self.get_host_triggers()

        for t in triggers:
            positive_expressions = []
            expression_ret_str = ''
            redis_alert_key = 'host_%s_trigger_%s' %(self.client_id,t.id)
            alert_data_in_redis = self.redis_obj.get(redis_alert_key)
            redis_key_flag = False
            if alert_data_in_redis:
                redis_key_flag = True
            for expression in t.triggerexpression_set.select_related().order_by('id'):
                expression_ret = self.deal_expression(expression)
                if expression_ret:
                    expression_ret_str += str(expression_ret[0])
                    if expression_ret[0]:
                        expression_ret.insert(1,expression.service_index.key)
                        expression_ret.insert(1,expression.data_calc_func)
                        expression_ret.insert(1,expression.service.name)
                        positive_expressions.append(expression_ret)
                    if expression.logic_type:
                        expression_ret_str += " "+expression.logic_type+" "

            notify_flag = eval(expression_ret_str)
            recover_data = ''
            if notify_flag:
                if redis_key_flag:
                    notify_data = json.loads(alert_data_in_redis)
                else:
                    notify_data = {}
                    notify_data['client_id'] = self.client_id
                    notify_data['trigger_id'] = t.id
                    notify_data['trigger_name'] = t.name
                    notify_data['status'] = True
                notify_data['notify_detail'] = positive_expressions

                self.redis_obj.set(redis_alert_key,json.dumps(notify_data))
                print notify_data,'notify_data'

                self.mq_channel.queue_declare(queue='trigger_notify')
                self.mq_channel.basic_publish(exchange='', routing_key='trigger_notify', body=json.dumps(notify_data))
            else:
                if redis_key_flag:
                    # alert_data_in_redis = self.redis_obj.get(redis_alert_key)
                    alert_data_in_redis = json.loads(alert_data_in_redis)
                    alert_data_in_redis['status'] = False
                    self.redis_obj.set(redis_alert_key,json.dumps(alert_data_in_redis))
                    self.mq_channel.queue_declare(queue='trigger_notify')
                    self.mq_channel.basic_publish(exchange='', routing_key='trigger_notify', body=json.dumps(alert_data_in_redis))                    # self.redis_obj.delete(redis_alert_key)
            alert_dic = {}
            alert_dic['client_id'] = self.client_id

            self.mq_channel.queue_declare(queue='host_alive_notify')
            self.mq_channel.basic_publish(exchange='', routing_key='host_alive_notify', body=json.dumps(alert_dic))