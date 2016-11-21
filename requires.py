#!/usr/bin/python

from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes


class CNIPluginClient(RelationBase):
    scope = scopes.UNIT

    @hook('{requires:kubernetes-cni}-relation-{joined,changed}')
    def changed(self):
        ''' Indicate the relation is connected, and if the relation data is
        set it is also available. '''
        conv = self.conversation()
        conv.set_state('{relation_name}.connected')
        config = self.get_config()
        if config['is_master'] is True:
            self.set_state('{relation_name}.is-master')
        elif config['is_master'] is False:
            self.set_state('{relation_name}.is-worker')

    @hook('{requires:kubernetes-cni}-relation-{departed}')
    def broken(self):
        ''' Indicate the relation is no longer available and not connected. '''
        self.remove_state('{relation_name}.connected')
        # TODO: Remove more states?

    def get_config(self):
        ''' Get the kubernetes configuration information. '''
        conv = self.conversation()
        return {
            'is_master': conv.get_remote('is_master'),
            'kubeconfig_path': conv.get_remote('kubeconfig_path')
        }

    def set_available(self):
        conv = self.conversation()
        conv.set_remote(data = {
            'available': True
        })
