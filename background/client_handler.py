__author__ = 'zhaobin022'
from background import models

class ClientHandler(object):

    def get_service_from_template(self,templates):
        services = []
        for t in templates:
            services.extend(t.services.select_related())
        return services

    def get_configs(self,client_id):
        services = []
        client_configs = {'services':{}}
        host = models.Host.objects.get(id=client_id)
        templates_from_host = host.templates.select_related()
        services.extend(self.get_service_from_template(templates_from_host))

        for g in host.host_groups.select_related():
            t = g.templates.select_related()
            services.extend(self.get_service_from_template(t))

        services = set(services)
        print services
        for s in services:
            client_configs['services'][s.name] = [s.plugin_name,s.interval]


        return client_configs
