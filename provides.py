#!/usr/bin/python

from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes


class CNIPluginProvider(RelationBase):
    scope = scopes.UNIT

    @hook('{provides:kubernetes-cni}-relation-{joined,changed}')
    def joined_or_changed(self):
        ''' Set the connected state from the provides side of the relation. '''
        conv = self.conversation()
        conv.set_state('{relation_name}.connected')
        if conv.get_remote('available') is True:
            conv.set_state('{relation_name}.available')

    @hook('{provides:kubernetes-cni}-relation-{departed}')
    def broken_or_departed(self):
        '''Remove connected state from the provides side of the relation. '''
        conv = self.conversation()
        conv.remove_state('{relation_name}.connected')
        conv.remove_state('{relation_name}.available')

    def set_config(self, is_master, kubeconfig_path):
        ''' Relays a dict of kubernetes configuration information. '''
        conv = self.conversation()
        conv.set_remote(data = {
            'is_master': is_master,
            'kubeconfig_path': kubeconfig_path
        })
