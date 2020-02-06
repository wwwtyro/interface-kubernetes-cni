from unittest.mock import MagicMock

import requires


def test_get_config():
    client = requires.CNIPluginClient()
    config = {
        'is_master': False,
        'kubeconfig_path': '/path/to/kubeconfig'
    }
    client.all_joined_units.received_raw = config
    assert client.get_config() == config


def test_set_config():
    client = requires.CNIPluginClient()
    client.relations = [MagicMock(), MagicMock()]
    client.set_config('192.168.0.0/24', '10-test.conflist')
    for relation in client.relations:
        relation.to_publish_raw.update.assert_called_once_with({
            'cidr': '192.168.0.0/24',
            'cni-conf-file': '10-test.conflist'
        })
