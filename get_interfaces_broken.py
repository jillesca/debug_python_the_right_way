"""Fetch interface list from an IOS-XR device via gNMI and parse OpenConfig data."""

import os

from pygnmi.client import gNMIclient


def get_interfaces(host: str, port: int, username: str, password: str) -> list:
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


def parse_interfaces(response: dict) -> list[dict]:
    """Parse gNMI response into a list of interface dictionaries."""
    interfaces = []

    for notification in response["notification"]:
        for update in notification["update"]:
            raw_interfaces = update["val"]["openconfig-interfaces:interface"]

            for intf in raw_interfaces:
                intf_name = intf["name"]
                state = intf["state"]

                interfaces.append(
                    {
                        "name": intf_name,
                        "admin_status": state["admin-status"],
                        "oper_status": state["oper-status"],
                        "description": intf.get("config", {}).get(
                            "description", ""
                        ),
                        "mtu": intf.get("config", {}).get("mtu", "N/A"),
                        "type": state["type"],
                    }
                )

    return interfaces


def display_interfaces(interfaces: list[dict]) -> None:
    """Print parsed interface data in a readable format."""
    print(
        f"\n{'Interface':<35} {'Admin':<10} {'Oper':<10} {'MTU':<8} {'Description'}"
    )
    print("-" * 90)

    for intf in interfaces:
        print(
            f"{intf['name']:<35} "
            f"{str(intf['admin_status']):<10} "
            f"{str(intf['oper_status']):<10} "
            f"{str(intf['mtu']):<8} "
            f"{intf['description']}"
        )

    print(f"\nTotal interfaces: {len(interfaces)}")


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
