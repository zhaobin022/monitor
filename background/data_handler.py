#_*_coding:utf-8_*_

__author__ = 'zhaobin022'
from monitor.settings import STATUS_DATA_OPTIMIZATION
import json
import time
import copy

class DataHandler(object):
    def __init__(self,client_id,service,data,REDIS_OBJ):
        self.client_id = client_id
        self.service_name = service.name
        self.service_check_interval = service.interval
        self.data = data
        self.redis_obj = REDIS_OBJ

    def get_redis_slice(self,redis_key , interval, service_check_interval):
        count = interval/service_check_interval
        count += 5
        ret_list = []
        redis_slice = self.redis_obj.lrange(redis_key,-count,-1)
        current_time = time.time()
        redis_slice.reverse()
        for s in redis_slice:
            data_point , timestamp = json.loads(s)
            if current_time - timestamp < interval:
                ret_list.append(s)
            else:
                break

        return ret_list

    def optimized_data(self,current_redis_key, redis_slice):
        one_data_point = redis_slice[0]
        one_data_point = json.loads(one_data_point)
        data = one_data_point[0]
        timestamp = one_data_point[1]
        temp_dic = {}
        if  'data' in data.keys():

            sub_data  = data['data']
            for k,v_dic in sub_data.items():
                # k like lo or eth0
                temp_dic[k] = {}
                for sub_key , sub_val in v_dic.items():
                    temp_dic[k][sub_key] = []
            ret_dic = copy.deepcopy(temp_dic)
            for p in redis_slice:
                p = json.loads(p)
                data , update_time = p
                for k,sub_dic in data['data'].items():
                    # k like lo or eth0
                    for sub_key,sub_val in sub_dic.items():
                        temp_dic[k][sub_key].append(round(float(sub_val),2))

            for k,sub_dic in temp_dic.items():
                for sub_key,sub_val in sub_dic.items():
                    avg_ret = self.get_avg(sub_val)
                    max_ret = self.get_max(sub_val)
                    min_ret = self.get_min(sub_val)
                    mid_ret = self.get_mid(sub_val)
                    ret_dic[k][sub_key] = [avg_ret,max_ret,min_ret,mid_ret]
            self.redis_obj.rpush(current_redis_key,json.dumps([{'data':ret_dic},time.time()] ))

        else:
            for key in data.keys():
                if key == 'status':continue
                temp_dic[key] = []

            ret = copy.deepcopy(temp_dic)
            for p in redis_slice:
                p = json.loads(p)
                point_data, update_time = p
                for k,v in point_data.items():
                    if k == 'status':continue
                    temp_dic[k].append(round(float(v),2))
            for k,v_list in temp_dic.items():
                avg_ret = self.get_avg(v_list)
                max_ret = self.get_max(v_list)
                min_ret = self.get_min(v_list)
                mid_ret = self.get_mid(v_list)
                ret[k] = [avg_ret,max_ret,min_ret,mid_ret]
            self.redis_obj.rpush(current_redis_key,json.dumps([ret,time.time()] ))

    def get_max(self,data_list):
        if len(data_list) > 0:
            return max(data_list)
        else:
            return 0

    def get_min(self,data_list):
        if len(data_list) > 0:
            return min(data_list)
        else:
            return 0

    def get_mid(self,data_list):
        if len(data_list) > 0:
            data_list.sort()
            return data_list[len(data_list)/2]

    def get_avg(self,data_list):
        if len(data_list) > 0:
            ret = sum(data_list)/len(data_list)
            ret = round(float(ret),2)
            return ret
        else:
            return 0

    def process(self):
        for time_range,time_range_list in STATUS_DATA_OPTIMIZATION.items():
            interval = time_range_list[0]
            count = time_range_list[1]
            current_redis_key = 'StatusData_%s_%s_%s' % (self.client_id,self.service_name,time_range)

            last_point_from_redis = self.redis_obj.lrange(current_redis_key,-1,-1)

            if not last_point_from_redis:
                self.redis_obj.rpush(current_redis_key,json.dumps([None,time.time()] ))
                continue
            last_point_from_redis = json.loads(last_point_from_redis[0])
            last_update_time = last_point_from_redis[1]
            if interval == 0:
                self.redis_obj.rpush(current_redis_key,json.dumps([self.data,time.time()] ))
            else:
                if time.time() - last_update_time > interval:
                    lastest_data_key_in_redis = "StatusData_%s_%s_latest" %(self.client_id,self.service_name)
                    redis_slice = self.get_redis_slice(lastest_data_key_in_redis,interval,self.service_check_interval)
                    if len(redis_slice)> 0:
                        self.optimized_data(current_redis_key, redis_slice)
            while self.redis_obj.llen(current_redis_key) > count:
                self.redis_obj.lpop(current_redis_key)


