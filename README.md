[![Release](https://github.com/happydev-ca/spypoint-home-assistant/actions/workflows/release.yml/badge.svg)](https://github.com/happydev-ca/spypoint-home-assistant/actions/workflows/release.yml)
[![Validate](https://github.com/happydev-ca/spypoint-home-assistant/actions/workflows/validate.yml/badge.svg)](https://github.com/happydev-ca/spypoint-home-assistant/actions/workflows/validate.yml)

# Spypoint Custom Integration for Home Assistant

Use to monitor your Spypoint cameras.

## Installation

### Automatic

[![Install from Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=happydev-ca&repository=spypoint-home-assistant&category=integration)

Or:

- Go to your Home Assistant
- Open [HACS](https://hacs.xyz/)
- Search for `Spypoint`
- Click the `Download` button on the bottom right
- Restart Home Assistant

### Manual

- Copy the `spypoint` folder your `/path/to/home-assistant/custom_components/` directory
- Restart Home Assistant

## Configuration

- Go to `Settings` -> `Devices & Services`
- Click on the `Integrations` tab
- Click the `Add Integration` button
- Search for Spypoint

<img alt="Configuration" src=".img/config.png" width="344"/>

Then click the `Submit` button. Your credentials will be validated, and your cameras will be created in Home Assistant.

*This custom integration does not support configuration through the `configuration.yaml` file.*

## Sensors

A device is created for each camera in your account.

<img alt="Device" height="" src="./.img/device.png" width="344"/>

The following sensors are created for each camera:

<img alt="Sensors" height="" src="./.img/sensors.png" width="344"/>


<img alt="Diagnostic" src="./.img/diagnostic.png" width="344"/>

## Development

### Test locally

```shell
make install
make test
```

### Run locally

```shell
# from ha core repo, setup ha core
script/setup
source venv/bin/activate

# create a symlink in config/custom_component folder to this folder
cd config/custom_components
ln -s ../../../spypoint-home-assistant/custom_components/spypoint .

# run
hass -c config

# view
open http://localhost:8123/
```

### Release version

```shell
make release bump=patch|minor|major
```