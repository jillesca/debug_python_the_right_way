# Debug Python the Right Way

Sample code for the video **"Debug Python the Right Way"** — published on the [Cisco DevNet YouTube channel](https://www.youtube.com/@CiscoDevNetchannel).

The script connects to an IOS-XR device via gNMI, retrieves OpenConfig interface data, and triggers a real `KeyError` that is solved step by step using the VS Code debugger.

## What's in this repo

| File / Folder              | Description                                                                                                                |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `get_interfaces.py`        | The **broken** script — crashes with `KeyError: 'openconfig-if-ethernet:ethernet'` on software interfaces (e.g. Loopback0) |
| `answer/get_interfaces.py` | The **fixed** script — uses `.get()` with an empty dict fallback to handle all interface types safely                      |
| `.vscode/launch.json`      | Debugger configuration — press **F5** to launch the debug session                                                          |
| `.vscode/settings.json`    | VS Code settings — points to the `.venv` created by `uv` and loads `.env` automatically                                    |
| `pyproject.toml`           | Project dependencies (`pygnmi`)                                                                                            |
| `.env`                     | Sandbox credentials (not committed) — see setup below                                                                      |

## Sandbox

This script targets the **IOS-XR Always-On DevNet Sandbox** — a free, public lab environment, no VPN required.

[https://devnetsandbox.cisco.com/DevNet](https://devnetsandbox.cisco.com/DevNet)

Search for **"IOS XR Always On"** to find the sandbox. The host, port, username, and password go in your `.env` file (see below).

## Setup

**Prerequisites:** [uv](https://docs.astral.sh/uv/) installed.

```bash
# Clone the repo
git clone https://github.com/jillesca/debug_python_the_right_way
cd debug_python_the_right_way

# Create the virtual environment and install dependencies
uv sync

# Create the .env file with sandbox credentials you got on your reservation
cat > .env <<EOF
GNMI_HOST=sandbox-iosxr-1.cisco.com
GNMI_PORT=57777
GNMI_USERNAME=admin
GNMI_PASSWORD=C1sco12345
EOF
```

## Running the script

**Broken version** (triggers the KeyError):

```bash
uv run get_interfaces.py
```

**Fixed version:**

```bash
uv run answer/get_interfaces.py
```

## Debugging in VS Code

The `.vscode/launch.json` is already configured. Open the repo in VS Code and press **F5** — the debugger launches the script with the correct interpreter and loads credentials from `.env` automatically.

### Debugging tools covered in the video

| Tool                              | What it does                                                                |
| --------------------------------- | --------------------------------------------------------------------------- |
| **Breakpoints + Variables panel** | Pause execution and inspect every local variable                            |
| **Watch expressions**             | Track specific values across loop iterations                                |
| **Debug Console (REPL)**          | Run any Python expression against live data while paused                    |
| **Conditional breakpoints**       | Break only when a condition is met — skip straight to the failing iteration |
| **Logpoints**                     | Log values to the debug console without modifying code                      |

## The bug explained

`get_interfaces.py` assumes every interface has an `openconfig-if-ethernet:ethernet` key. Physical interfaces (GigabitEthernet) do — but software interfaces like `Loopback0` don't. The fix is a single line:

```python
# Broken — crashes on Loopback0
eth_state = val["openconfig-if-ethernet:ethernet"]["state"]

# Fixed — safe fallback to empty dict
eth_state = val.get("openconfig-if-ethernet:ethernet", {}).get("state", {})
```
