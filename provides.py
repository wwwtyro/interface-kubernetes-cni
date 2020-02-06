#!/usr/bin/python

from charmhelpers.core import hookenv
from charms.reactive import Endpoint
from charms.reactive import when_any, when_not
from charms.reactive import set_state, remove_state


class CNIPluginProvider(Endpoint):

    @when_any('endpoint.{endpoint_name}.changed')
    def changed(self):
        ''' Set the connected state from the provides side of the relation. '''
        set_state(self.expand_name('{endpoint_name}.connected'))
        if self.config_available():
            set_state(self.expand_name('{endpoint_name}.available'))
        else:
            remove_state(self.expand_name('{endpoint_name}.available'))
        remove_state(self.expand_name('{endpoint_name}.configured'))
        remove_state(self.expand_name('endpoint.{endpoint_name}.changed'))

    @when_not('endpoint.{endpoint_name}.joined')
    def broken_or_departed(self):
        '''Remove connected state from the provides side of the relation. '''
        remove_state(self.expand_name('{endpoint_name}.connected'))
        remove_state(self.expand_name('{endpoint_name}.available'))
        remove_state(self.expand_name('{endpoint_name}.configured'))

    def set_config(self, is_master, kubeconfig_path):
        ''' Relays a dict of kubernetes configuration information. '''
        for relation in self.relations:
            relation.to_publish_raw.update({
                'is_master': is_master,
                'kubeconfig_path': kubeconfig_path
            })
        set_state(self.expand_name('{endpoint_name}.configured'))

    def config_available(self):
        ''' Ensures all config from the CNI plugin is available. '''
        goal_state = hookenv.goal_state()
        related_apps = [
            name for name in goal_state['relations'][self.endpoint_name]
            if '/' not in name
        ]
        if not related_apps:
            return False
        configs = self.get_configs()
        return all(
            'cidr' in config and 'cni-conf-file' in config
            for config in [
                configs.get(related_app, {}) for related_app in related_apps
            ]
        )

    def get_config(self, default=None):
        configs = self.get_configs()
        if default and default not in configs:
            msg = 'relation not found for default CNI %s, ignoring' % default
            hookenv.log(msg, level='WARN')
            return self.get_config()
        elif default:
            return configs.get(default)
        else:
            return configs[sorted(configs)[0]]

    def get_configs(self):
        return {
            relation.application_name: relation.joined_units.received_raw
            for relation in self.relations if relation.application_name
        }
