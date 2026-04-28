"""Tests for get_interfaces — parsing and display logic."""

from answer.get_interfaces import parse_interfaces, _simplify_type


def _build_response(*interfaces):
    """Helper: wrap interface dicts into the gNMI notification structure."""
    updates = [{"val": intf} for intf in interfaces]
    return {"notification": [{"update": updates}]}


def test_parse_interfaces_handles_ethernet_and_loopback():
    """parse_interfaces returns entries for both Ethernet and Loopback types."""
    response = _build_response(
        {
            "name": "GigabitEthernet0/0/0/0",
            "state": {
                "admin-status": "UP",
                "oper-status": "UP",
                "mtu": 1514,
                "type": "iana-if-type:ethernetCsmacd",
                "counters": {"in-pkts": 100, "out-pkts": 200},
            },
            "config": {"description": "uplink"},
            "openconfig-if-ethernet:ethernet": {
                "state": {
                    "port-speed": "1Gbps",
                    "mac-address": "00:11:22:33:44:55",
                }
            },
        },
        {
            "name": "Loopback0",
            "state": {
                "admin-status": "UP",
                "oper-status": "UP",
                "mtu": 1500,
                "type": "iana-if-type:softwareLoopback",
                "counters": {"in-pkts": 0, "out-pkts": 0},
            },
            "config": {"description": "management"},
        },
    )

    interfaces = parse_interfaces(response)

    assert len(interfaces) == 2
    assert interfaces[0]["name"] == "GigabitEthernet0/0/0/0"
    assert interfaces[0]["port_speed"] == "1Gbps"
    assert interfaces[1]["name"] == "Loopback0"
    assert interfaces[1]["port_speed"] == ""


def test_simplify_type_maps_known_and_unknown():
    """_simplify_type returns short labels for known types and strips prefix for unknown."""
    assert _simplify_type("iana-if-type:ethernetCsmacd") == "Ethernet"
    assert _simplify_type("iana-if-type:softwareLoopback") == "Loopback"
    assert _simplify_type("iana-if-type:unknown") == "unknown"
