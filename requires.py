#!/usr/bin/python

from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes


class CNIPluginClient(RelationBase):
    scope = scopes.GLOBAL

    @hook('{requires:kubernetes-cni}-relation-{joined,changed}')
    def changed(self):
        ''' Indicate the relation is connected, and if the relation data is
        set it is also available. '''
        self.set_state('{relation_name}.connected')
        config = self.get_config()
        if config['is_master'] == 'True':
            self.set_state('{relation_name}.is-master')
            self.set_state('{relation_name}.configured')
        elif config['is_master'] == 'False':
            self.set_state('{relation_name}.is-worker')
            self.set_state('{relation_name}.configured')
        else:
            self.remove_state('{relation_name}.configured')

    @hook('{requires:kubernetes-cni}-relation-{departed}')
    def broken(self):
        ''' Indicate the relation is no longer available and not connected. '''
        self.remove_state('{relation_name}.connected')
        self.remove_state('{relation_name}.is-master')
        self.remove_state('{relation_name}.is-worker')
        self.remove_state('{relation_name}.configured')

    def get_config(self):
        ''' Get the kubernetes configuration information. '''
        return {
            'is_master': self.get_remote('is_master'),
            'kubeconfig_path': self.get_remote('kubeconfig_path')
        }

    def set_config(self, cidr):
        ''' Sets the CNI configuration information. '''
        self.set_remote(data={
            'cidr': cidr
        })
