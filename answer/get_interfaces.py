"""Fetch interface list from an IOS-XR device via gNMI and parse OpenConfig data."""

import os

from pygnmi.client import gNMIclient

_TYPE_MAP = {
    "iana-if-type:ethernetCsmacd": "Ethernet",
    "iana-if-type:softwareLoopback": "Loopback",
    "iana-if-type:other": "Other",
    "iana-if-type:null": "Null",
}


def get_interfaces(host: str, port: int, username: str, password: str) -> dict:
    """Connect to a device via gNMI and retrieve interface information."""
    with gNMIclient(
        target=(host, port),
        username=username,
        password=password,
        insecure=True,
    ) as gc:
        response = gc.get(
            path=["openconfig-interfaces:interfaces/interface"],
            encoding="json_ietf",
        )

    return response


def _get_ip_address(val: dict) -> str:
    """Extract the primary IPv4 address/prefix from subinterfaces, if present."""
    subifs = val.get("subinterfaces", {}).get("subinterface", [])
    for subif in subifs:
        ipv4 = subif.get("openconfig-if-ip:ipv4", {})
        addresses = ipv4.get("addresses", {}).get("address", [])
        for addr in addresses:
            state = addr.get("state", {})
            if state.get("type") == "PRIMARY":
                ip = state.get("ip", "")
                prefix = state.get("prefix-length", "")
                if ip:
                    return f"{ip}/{prefix}" if prefix else ip
    return ""


def _simplify_type(raw_type: str) -> str:
    """Convert IANA interface type to a short human-readable label."""
    return _TYPE_MAP.get(
        raw_type, raw_type.split(":")[-1] if ":" in raw_type else raw_type
    )


def parse_interfaces(response: dict) -> list[dict]:
    """Parse gNMI response into a list of interface dictionaries.

    Each update in the gNMI notification represents one interface, where
    update['val'] is the full interface object (not a wrapper list).
    """
    interfaces = []

    for notification in response.get("notification", []):
        for update in notification.get("update", []):
            val = update.get("val", {})
            if not isinstance(val, dict) or "name" not in val:
                continue

            state = val.get("state", {})
            config = val.get("config", {})
            counters = state.get("counters", {})
            eth_state = val.get("openconfig-if-ethernet:ethernet", {}).get(
                "state", {}
            )

            interfaces.append(
                {
                    "name": val["name"],
                    "admin_status": state.get("admin-status", "N/A"),
                    "oper_status": state.get("oper-status", "N/A"),
                    "description": config.get(
                        "description", state.get("description", "")
                    ),
                    "mtu": state.get("mtu", "N/A"),
                    "type": _simplify_type(
                        state.get("type", config.get("type", "N/A"))
                    ),
                    "ip_address": _get_ip_address(val),
                    "in_pkts": counters.get("in-pkts", "N/A"),
                    "out_pkts": counters.get("out-pkts", "N/A"),
                    "in_errors": counters.get("in-errors", "0"),
                    "out_errors": counters.get("out-errors", "0"),
                    "port_speed": eth_state.get("port-speed", ""),
                    "mac_address": eth_state.get("mac-address", ""),
                }
            )

    return interfaces


def display_interfaces(interfaces: list[dict]) -> None:
    """Print parsed interface data as two tables: status/config and counters."""
    print(f"\n{'=' * 100}")
    print(
        f"  INTERFACE STATUS & CONFIGURATION  ({len(interfaces)} interfaces)"
    )
    print(f"{'=' * 100}")
    print(
        f"{'Interface':<26} {'Type':<10} {'Admin':<7} {'Oper':<7} "
        f"{'MTU':<6} {'IP Address':<20} {'Description'}"
    )
    print("-" * 100)

    for intf in interfaces:
        print(
            f"{intf['name']:<26} "
            f"{intf['type']:<10} "
            f"{intf['admin_status']:<7} "
            f"{intf['oper_status']:<7} "
            f"{str(intf['mtu']):<6} "
            f"{intf['ip_address']:<20} "
            f"{intf['description']}"
        )

    print(f"\n{'=' * 100}")
    print("  TRAFFIC COUNTERS")
    print(f"{'=' * 100}")
    print(
        f"{'Interface':<26} {'In Pkts':>12} {'Out Pkts':>12} "
        f"{'In Errors':>10} {'Out Errors':>11} {'Speed':<14} {'MAC Address'}"
    )
    print("-" * 100)

    for intf in interfaces:
        print(
            f"{intf['name']:<26} "
            f"{str(intf['in_pkts']):>12} "
            f"{str(intf['out_pkts']):>12} "
            f"{str(intf['in_errors']):>10} "
            f"{str(intf['out_errors']):>11} "
            f"{intf['port_speed']:<14} "
            f"{intf['mac_address']}"
        )

    print()


def main() -> None:
    """Main entry point — reads config from environment variables."""
    host = os.environ.get("GNMI_HOST", "sandbox-iosxr-1.cisco.com")
    port = int(os.environ.get("GNMI_PORT", "57777"))
    username = os.environ.get("GNMI_USER", "admin")
    password = os.environ.get("GNMI_PASS", "C1sco12345")

    print(f"Connecting to {host}:{port} via gNMI...")
    response = get_interfaces(host, port, username, password)

    print("Parsing interface data...")
    interfaces = parse_interfaces(response)

    display_interfaces(interfaces)


if __name__ == "__main__":
    main()
