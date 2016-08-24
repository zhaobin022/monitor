__author__ = 'zhaobin022'

import pika
import sys
import os
from argparse import ArgumentParser
import json
import redis
import time
import threading

class ActionHandler(object):
    def __init__(self):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitor.settings")
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(BASE_DIR)
        import django
        django.setup()
        from background import models
        from monitor import settings as django_settings
        from utils.sendmail_tools import sendmail
        from django.core.cache import cache
        self.cache = cache
        self.django_settings = django_settings
        pool = redis.ConnectionPool(host=django_settings.REDIS_CONN['HOST'], port=django_settings.REDIS_CONN['PORT'])
        self.redis_obj = redis.Redis(connection_pool=pool)
        self.models = models
        self.sendmail = sendmail
        self.alert_dic = {}
        self.host_alive_dic = {}

    def listen_notify_mq_channel(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                       'localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='trigger_notify')

        channel.basic_consume(self.callback, queue='trigger_notify', no_ack=True)
        print ' [*] Waiting for trigger notify messages. To exit press CTRL+C'
        channel.start_consuming()



    def check_host_alive_callback(self,ch, method, properties, body):
        print body,'in check_host_alive_callback'
        data = json.loads(body)
        client_id = data['client_id']
        self.host_alive_dic['client_id'] = time.time()
        for client_id,time_stamp in self.host_alive_dic.items():
            if time.time() - time_stamp > self.django_settings.HOST_TIMEOUT_SECOND:
                pass




    def listen_host_alive_channel(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                       'localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='host_alive_notify')

        channel.basic_consume(self.check_host_alive_callback, queue='host_alive_notify', no_ack=True)
        print ' [*] Waiting for host alive messages. To exit press CTRL+C'
        channel.start_consuming()

    def process(self):
        # self.listen_notify_mq_channel()
        listener_trigger_thread = threading.Thread(target=self.listen_notify_mq_channel,args=())
        listener_trigger_thread.start()

        listener_host_alive_thread = threading.Thread(target=self.listen_host_alive_channel,args=())
        listener_host_alive_thread.start()




    def get_action_set(self,trigger_id,client_id):
        action_list = []
        trigger_obj = self.models.Trigger.objects.get(id=trigger_id)
        if trigger_obj:
            actions = trigger_obj.action_set.select_related()
            action_list.extend(actions)
        client_obj = self.models.Host.objects.get(id=client_id)
        for hg in client_obj.host_groups.select_related():
            actions = hg.action_set.select_related()
            if actions:
                action_list.extend(actions)

        actions = client_obj.action_set.select_related()
        action_list.extend(actions)
        action_set = set(action_list)
        return action_set


    def execute_email(self,action_operation,subject,msg):
        to_list = []
        for user_profile in action_operation.notifiers.select_related():
            to_list.append(user_profile.email)

        self.sendmail(to_list,subject,msg)

    def execute_sms(self,msg):
        pass

    def execute_script(self,msg):
        pass
    def iter_action(self,redis_alert_key,alert_dic):
        host = self.models.Host.objects.get(id=alert_dic['client_id'])
        trigger = self.models.Trigger.objects.get(id=alert_dic['trigger_id'])

        subject = 'hostname : {hostname},ip : {ip}'.format(
            hostname=host.name,
            ip = host.ip_addr,
        )

        mail_body=''
        notify_detail =  alert_dic['notify_detail']
        for i in notify_detail:
            mail_body+='''
service_name : %s
severity : %s
calculation_function : %s
service_key : %s
service_key_number : %d
sub_key : %s
        ''' % (i[1],trigger.get_severity_display(),i[2],i[3],i[4],str(i[5]))


        if alert_dic['status'] == True:
            for action in self.get_action_set(alert_dic['trigger_id'],alert_dic['client_id']):
                if time.time() - alert_dic['last_alert_time'] > action.interval:
                    alert_dic['alert_count'] += 1
                    alert_dic['last_alert_time'] = time.time()
                    self.redis_obj.set(redis_alert_key,json.dumps(alert_dic))
                    for action_operation in action.operations.select_related():
                        if alert_dic['alert_count'] >= action_operation.step:
                            action_operation_func = getattr(self,'execute_%s' % action_operation.action_type)
                            action_operation_func(action_operation,subject,mail_body)

        elif alert_dic['status']  == False:
            subject = 'RECOVER hostname : {hostname},ip : {ip}'.format(
                hostname=host.name,
                ip = host.ip_addr,
            )
            mail_body=''
            for i in notify_detail:
                mail_body+='''
service_name : %s
severity : %s
calculation_function : %s
service_key : %s
sub_key : %s
            ''' % (i[1],trigger.get_severity_display(),i[2],i[3],str(i[5]))
            self.execute_action(client_id=alert_dic['client_id'],trigger_id=alert_dic['trigger_id'],subject=subject,mail_body=mail_body)
            self.redis_obj.delete(redis_alert_key)

    def execute_action(self,client_id,trigger_id,subject,mail_body):
        for action in self.get_action_set(trigger_id,client_id):
            for action_operation in action.operations.select_related():
                action_operation_func = getattr(self,'execute_%s' % action_operation.action_type)
                action_operation_func(action_operation,subject,mail_body)

    def callback(self,ch, method, properties, body):
        print body
        alert_data = json.loads(body)
        trigger_id = alert_data.get('trigger_id')
        client_id = alert_data.get('client_id')
        if trigger_id:
            redis_alert_key = 'host_%s_trigger_%s' %(client_id,trigger_id)
            alert_data_in_redis = self.redis_obj.get(redis_alert_key)
            if alert_data_in_redis:
                alert_data = json.loads(alert_data_in_redis)
                if alert_data['status'] == True:
                    if not alert_data.has_key('alert_count'):
                        alert_data['alert_count'] = 0
                        alert_data['last_alert_time'] = 0
                self.redis_obj.set(redis_alert_key,json.dumps(alert_data))
            self.iter_action(redis_alert_key,alert_data)

        else:
            print 'invaild alert data format .'


if __name__ == '__main__':
    parser = ArgumentParser(usage='%(prog)s  start/stop')
    parser.add_argument(
        'choice',
        help="give one choice start or stop",
        choices=('start', 'stop')
    )

    args = parser.parse_args()
    if args.choice == 'start':
        action_handler = ActionHandler()
        action_handler.process()
    elif args.choice == 'stop':
        pass
    else:
        parser.print_help()




