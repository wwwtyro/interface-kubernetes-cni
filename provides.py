#!/usr/bin/python

from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes


class CNIPluginProvider(RelationBase):
    scope = scopes.GLOBAL

    @hook('{provides:kubernetes-cni}-relation-{joined,changed}')
    def joined_or_changed(self):
        ''' Set the connected state from the provides side of the relation. '''
        self.set_state('{relation_name}.connected')
        if self.config_available():
            self.set_state('{relation_name}.available')

    @hook('{provides:kubernetes-cni}-relation-{departed}')
    def broken_or_departed(self):
        '''Remove connected state from the provides side of the relation. '''
        self.remove_state('{relation_name}.connected')
        self.remove_state('{relation_name}.available')
        self.remove_state('{relation_name}.configured')

    def set_config(self, is_master, kubeconfig_path):
        ''' Relays a dict of kubernetes configuration information. '''
        self.set_remote(data={
            'is_master': is_master,
            'kubeconfig_path': kubeconfig_path
        })
        self.set_state('{relation_name}.configured')

    def config_available(self):
        ''' Ensures all config from the CNI plugin is available. '''
        if not self.get_remote('cidr'):
            return False
        return True

    def get_config(self):
        ''' Returns all config from the CNI plugin. '''
        return {
            'cidr': self.get_remote('cidr'),
        }
