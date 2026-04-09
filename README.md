# DVI Smart Control for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Home Assistant integration for [DVI Energi](https://dvienergi.com/) heat pumps via the [Smart Control](https://smartcontrol.dvienergi.com) web portal.

There is no official API — this integration scrapes the web portal to expose sensors and controls in Home Assistant.

## Features

### Sensors
- Outdoor, tank, hot water, heating flow/return, and room temperatures
- Energy consumed and delivered (kWh and kW)
- Flow rate
- Compressor, hot water, and supplementary heat operating hours
- Current error list
- Last data update timestamp

### Binary sensors
- Compressor running
- Fan running
- Active errors indicator

### Controls
- **Switches**: Heating system on/off, hot water on/off, pump power on/off
- **Numbers**: Hot water temperature setpoint (5-55 °C), heating temperature offset (0-20)
- **Selects**: Hot water clock mode (clock / constant on / constant off), supplementary heating mode (off / automatic / reserve)

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu (top right) and select **Custom repositories**
3. Add `https://github.com/JakobHP/HA-DVISmartControl` with category **Integration**
4. Search for "DVI Smart Control" in HACS and install it
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/dvi_smart_control` folder into your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & services** > **Add integration**
2. Search for **DVI Smart Control**
3. Enter the email and password you use to log in at [smartcontrol.dvienergi.com](https://smartcontrol.dvienergi.com)

The integration polls the portal every 60 seconds. Commands (toggling switches, changing setpoints) may take up to 30 seconds to complete — this is a limitation of the DVI portal itself.

## Notes

- Requires a DVI Smart Control account at [smartcontrol.dvienergi.com](https://smartcontrol.dvienergi.com)
- The integration maintains a session with the portal and re-authenticates automatically if the session expires
- If your credentials change, Home Assistant will prompt you to re-authenticate

## License

[MIT](LICENSE)
