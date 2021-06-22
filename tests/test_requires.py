from charms.reactive import clear_flag, is_flag_set

import requires


def test_get_config():
    client = requires.CNIPluginClient("cni", [1])
    config = {"is_master": False}
    client.all_joined_units.received_raw = config
    assert client.get_config() == config


def test_set_config():
    client = requires.CNIPluginClient("cni", [1])
    client.set_config("192.168.0.0/24", "10-test.conflist")
    assert client.relations[0].to_publish_raw == {
        "cidr": "192.168.0.0/24",
        "cni-conf-file": "10-test.conflist",
    }


def test_manage_flags():
    client = requires.CNIPluginClient("cni", [1])
    client.all_joined_units.received_raw["kubeconfig-hash"] = "hash"
    client.manage_flags()
    assert is_flag_set("cni.kubeconfig.available")
    assert is_flag_set("cni.kubeconfig.changed")

    clear_flag("cni.kubeconfig.changed")
    client.manage_flags()
    assert is_flag_set("cni.kubeconfig.available")
    assert not is_flag_set("cni.kubeconfig.changed")
