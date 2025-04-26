# IPMI Control - Home Assistant Integration

Control servers via IPMI directly from Home Assistant!

## Features
- Power ON
- Power OFF
- Force RESET (reboot)
- Live server status
- Auto-refresh status every 2 minutes

## Installation
1. Copy the `custom_components/ipmi_control` folder into your Home Assistant `/config/custom_components/`.
2. Restart Home Assistant.
3. Configure `configuration.yaml`:

```yaml
switch:
  - platform: ipmi_control
    servers:
      - name: My IPMI Server
        host: 192.168.1.100
        user: ADMIN
        password: ADMIN
```

4. (Optional) Install via [HACS](https://hacs.xyz/).

## Services
You can use a service to RESET (reboot) a server:
- Service: `ipmi_control.reset_server`
- Data: `{ "entity_id": "switch.my_ipmi_server" }`

## Requirements
- Python library `pyghmi` (auto-installed).

## Author
Maintained by [Ton Nom ou Pseudo](https://github.com/ton_github).
