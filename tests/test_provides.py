from unittest.mock import MagicMock
import charmhelpers
import charms

import provides


def test_set_config():
    provider = provides.CNIPluginProvider()
    provider.relations = [MagicMock(), MagicMock()]
    provider.set_config(False, '/path/to/kubeconfig')
    for relation in provider.relations:
        relation.to_publish_raw.update.assert_called_once_with({
            'is_master': False,
            'kubeconfig_path': '/path/to/kubeconfig'
        })
    charms.reactive.set_flag.assert_called_once_with(
        'cni.configured'
    )


def test_get_configs():
    provider = provides.CNIPluginProvider()
    provider.relations = [MagicMock(), MagicMock()]
    provider.relations[0].application_name = 'app0'
    provider.relations[0].joined_units.received_raw = {
        'cidr': '192.168.0.0/16'
    }
    provider.relations[1].application_name = None
    config = provider.get_configs()
    assert config == {'app0': {'cidr': '192.168.0.0/16'}}


def test_get_config():
    provider = provides.CNIPluginProvider()
    provider.relations = [MagicMock(), MagicMock()]
    provider.relations[0].application_name = 'app0'
    provider.relations[0].joined_units.received_raw = {
        'cidr': '192.168.0.0/24'
    }
    provider.relations[1].application_name = 'app1'
    provider.relations[1].joined_units.received_raw = {
        'cidr': '192.168.1.0/24'
    }
    assert provider.get_config() == {'cidr': '192.168.0.0/24'}
    assert provider.get_config('app0') == {'cidr': '192.168.0.0/24'}
    assert provider.get_config('app1') == {'cidr': '192.168.1.0/24'}


def test_config_available():
    provider = provides.CNIPluginProvider()
    provider.relations = [MagicMock(), MagicMock()]
    provider.relations[0].application_name = 'app0'
    provider.relations[1].application_name = 'app1'

    def set_base_data():
        charmhelpers.core.hookenv.goal_state.return_value = {
            'relations': {
                'cni': {
                    'app0': 'foo',
                    'app1': 'foo',
                }
            }
        }
        provider.relations[0].joined_units.received_raw = {
            'cidr': '192.168.0.0/24',
            'cni-conf-file': '10-app0.conflist'
        }
        provider.relations[1].joined_units.received_raw = {
            'cidr': '192.168.1.0/24',
            'cni-conf-file': '10-app1.conflist'
        }

    # if there are no cni relations, then config is not available yet
    set_base_data()
    goal_state = charmhelpers.core.hookenv.goal_state()
    goal_state['relations'] = {}
    assert not provider.config_available()

    # if there are no related cni apps, then config is not available yet
    set_base_data()
    goal_state = charmhelpers.core.hookenv.goal_state()
    goal_state['relations']['cni'] = {}
    assert not provider.config_available()

    # if goal_state shows an app that's missing from relations, then config
    # is not available yet
    set_base_data()
    goal_state = charmhelpers.core.hookenv.goal_state()
    goal_state['relations']['cni']['app2'] = 'foo'
    assert not provider.config_available()

    # if cidr is missing from any related app, then config is not available
    for i in range(2):
        set_base_data()
        del provider.relations[i].joined_units.received_raw['cidr']
        assert not provider.config_available()

    # if cni-conf-file is missing from any related app, then config is not
    # available
    for i in range(2):
        set_base_data()
        del provider.relations[i].joined_units.received_raw['cni-conf-file']
        assert not provider.config_available()

    # otherwise, config is available
    set_base_data()
    assert provider.config_available()
