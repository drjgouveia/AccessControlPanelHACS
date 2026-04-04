# Access Control Panel - Home Assistant Integration

Home Assistant integration for the [BOS Keyboard Access Control Panel](https://github.com/bos_keyboard/access_control_panel) — a WiFi-enabled door access control system built on Raspberry Pi Pico W.

## Features

- **Alarm Control Panel** — Arm, disarm, and monitor alarm state
- **Access Log Sensor** — View recent access attempts with timestamps
- **Status Sensors** — Armed status, alarm status, user count
- **Lock Switches** — Control door locks per division (lock/unlock/open)
- **User Management** — Add, remove, update users and manage division access via services
- **Lovelace Dashboard** — Pre-built cards for full UI management

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right → **Custom repositories**
3. Add the repository URL, select **Integration**
4. Search for **Access Control Panel** and install
5. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/access_control_panel/` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **Access Control Panel**
3. Enter your device details:

| Field | Description | Default |
|-------|-------------|---------|
| **Host** | IP address of the Pico W device | — |
| **Port** | HTTP port of the web server | `80` |
| **Scan Interval** | How often to poll the device (seconds) | `10` |

4. The integration validates the connection before saving

## Entities

### Alarm Control Panel

| Entity | Description |
|--------|-------------|
| `alarm_control_panel.<device_name>` | Main alarm entity with arm/disarm/trigger support |

### Sensors

| Entity | Description | Attributes |
|--------|-------------|------------|
| `sensor.access_log` | Most recent access event | `entries` — list of last 10 log entries |
| `sensor.armed_status` | `Armed` or `Disarmed` | — |
| `sensor.alarm_status` | `Triggered` or `Normal` | — |
| `sensor.registered_users` | Number of registered users | `users` — list of all users with details |

### Switches

| Entity | Description |
|--------|-------------|
| `switch.lock_<division>` | One switch per configured division (lock/unlock) |

## Services

### `access_control_panel.send_code`

Send an access code to the keypad remotely.

```yaml
service: access_control_panel.send_code
data:
  code: "1234"
```

### `access_control_panel.add_user`

Add a new user to the system.

```yaml
service: access_control_panel.add_user
data:
  user_id: john_doe
  name: John Doe
  user_code: "5678"
  passcode: "secret123"
  access_level: 1
  divisions:
    - server_room
    - office
```

### `access_control_panel.remove_user`

Remove a user from the system.

```yaml
service: access_control_panel.remove_user
data:
  user_id: john_doe
```

### `access_control_panel.update_user`

Update user attributes.

```yaml
service: access_control_panel.update_user
data:
  user_id: john_doe
  name: John Smith
  access_level: 2
  enabled: true
```

### `access_control_panel.grant_division`

Grant a user access to a division.

```yaml
service: access_control_panel.grant_division
data:
  user_id: john_doe
  division: server_room
```

### `access_control_panel.revoke_division`

Revoke a user's access to a division.

```yaml
service: access_control_panel.revoke_division
data:
  user_id: john_doe
  division: server_room
```

### `access_control_panel.control_lock`

Control a door lock.

```yaml
service: access_control_panel.control_lock
data:
  division: main_entrance
  action: unlock
```

**Available actions:** `lock`, `unlock`, `open`, `toggle`

## Lovelace Dashboard

A pre-built dashboard with three views is included:

1. **Access Control Panel** — System status, alarm panel, quick actions, access log, user list
2. **User Management** — Instructions and quick actions for managing users
3. **Lock Control** — All lock switches with quick lock/unlock buttons

### Installation

1. Go to **Settings** → **Dashboards** → **Add Dashboard**
2. Choose **YAML mode**
3. Copy the contents of `lovelace/access_control_dashboard.yaml` into the configuration
4. Alternatively, import individual cards through the UI editor

### Example Card

```yaml
type: alarm-panel
entity: alarm_control_panel.access_control_panel
name: Front Door
states:
  - arm_home
  - disarm
```

## Automations

### Auto-lock after access granted

```yaml
alias: Auto-lock after access
trigger:
  - platform: state
    entity_id: sensor.access_log
condition:
  - condition: template
    value_template: "{{ state_attr('sensor.access_log', 'entries')[-1].granted }}"
action:
  - service: access_control_panel.control_lock
    data:
      division: main_entrance
      action: lock
```

### Notify on denied access

```yaml
alias: Notify on denied access
trigger:
  - platform: state
    entity_id: sensor.access_log
condition:
  - condition: template
    value_template: "{{ not state_attr('sensor.access_log', 'entries')[-1].granted }}"
action:
  - service: notify.mobile_app_your_phone
    data:
      title: "Access Denied"
      message: >
        {{ state_attr('sensor.access_log', 'entries')[-1].action }}
        at {{ state_attr('sensor.access_log', 'entries')[-1].time }}
```

### Arm alarm when everyone leaves

```yaml
alias: Arm alarm when home empty
trigger:
  - platform: state
    entity_id: zone.home
    to: "0"
action:
  - service: alarm_control_panel.alarm_arm_home
    target:
      entity_id: alarm_control_panel.access_control_panel
```

## Troubleshooting

### Cannot connect to device

- Verify the Pico W is powered on and connected to WiFi
- Check the IP address is correct and reachable from your Home Assistant network
- Ensure no firewall is blocking port 80

### Entities not appearing

- Check the device is responding at `http://<host>/api/status`
- Increase the scan interval if the device is slow to respond
- Check Home Assistant logs for errors under **Settings** → **System** → **Logs**

### Lock switches not showing

- Locks are created dynamically based on divisions configured on the device
- Ensure divisions are initialized in the firmware `main.py`
- Reconfigure the integration to refresh the entity list

## Requirements

- Home Assistant 2024.1.0 or later
- BOS Keyboard Access Control Panel firmware running on Raspberry Pi Pico W
- Device must be on the same network as Home Assistant
