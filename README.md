<h1 align="center">Taiwan Real-time Earthquake Monitoring for HA</h1>

![Logo](https://raw.githubusercontent.com/J1A-T13N/ha-trem/main/docs/media/logo.png)

[![License][license-shield]](LICENSE)
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![pre-commit][pre-commit-shield]][pre-commit]
[![GitHub Release][releases-shield]][releases]

[![hacs_custom][hacs_custom_shield]][hacs_custom]

[![Project Maintenance][maintenance-shield]][user_profile]
[![Project Maintenance][maintenance2-shield]][user2_profile]
<hr>

English | [繁體中文](README_zhHant.md)<br>

> [!IMPORTANT]
> This custom component installation is considered advanced<br>
> should only be used if one is an expert in managing a Linux operating system.


## Screenshots

![image](https://github.com/J1A-T13N/ha-trem/assets/29163857/620d2723-1d77-4ead-a203-6d0d612031fd)

<hr>
<br>


## Available

| Environment | Home Assistant OS[^1] | Home Assistant Core | Home Assistant Supervisor |
| :------------: | :------------: | :------------: | :------------: |
| Virtual Machine[^2] | :heavy_check_mark: |  |  |
| Container |  | :heavy_check_mark: | :question:[^3] |
| Virtual Environment |  | :heavy_check_mark: |  |
| Physics Machine[^4] | :question:[^5] | :heavy_minus_sign:[^6] | :question:[^3] |

:heavy_check_mark: Available<br>
:heavy_multiplication_x: Unavailable<br>
:question: Untested<br>
:heavy_minus_sign: See footnotes<br>
[^1]: /tmp is mounted noexec on HAOS so it can't compile, A [workaround](https://github.com/home-assistant/core/issues/118717) is to do this inside the container.
[^2]: Virtual Machine may include but not limited to: VirtualBox、Unraid、KVM/Proxmox、UTM...etc.
[^3]: If your installation method is [it](https://github.com/home-assistant/supervised-installer).
[^4]: Physics Machine may include but not limited to: Raspberry Pi、Home Assistant Green、Home Assistant Yellow...etc.
[^5]: So far, only known raspberry pi 4 is available.
[^6]: If your installation method on other systems, Hope you can provide feedback.

<hr>
<br>


## Installation

### Using [HACS](https://hacs.xyz/) (recommended)
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=J1A-T13N&repository=ha-trem&category=Integration)

### Manual
1. Create `config/custom_components` folder if not existing.
2. Copy `trem` into `custom_components` folder.

<hr>
<br>


## Config

```yaml
sensor:
  - platform: trem
    friendly_name: Company # Display name
    region: 116 # Region Code (Zip Code)
  - platform: trem
    friendly_name: Sweet Home # Display name
    keep_alive: True
    region: 231 # Region Code (Zip Code)
```
> [!TIP]
> This configuration is suitable for v0.0.2 and above versions<br>
> Release v0.0.1 Please change `friendly_name` back to `name`.
<br>

**:zap: Remember restart Home Assistant. :zap:**

<hr>
<br>


## Options

| Name                  | Type             | Requirement  | Description                                                                                                                                                                                                                       | Default   |
| --------------------- | ---------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| region                | string           | **Required** | Region Code can be found [here](https://github.com/ExpTechTW/TREM-tauri/blob/main/src/assets/json/region.json)                                                                                                                    |           |
| friendly_name         | string           | **Optional** | you want to display the name on Home Assistant                                                                                                                                                                                    | `Taiwan Real-time Earthquake Monitoring`      |
| keep_alive            | boolean          | **Optional** | Keep recent alert data                                                                                                                                                                                                            | `false` |

*An example of `configuration.yaml` can be found [here](configuration.yaml).*<br>

<hr>
<br>


## Known issues

1. HAOS unable to install dependencies is fix, See [here](docs/haos_guide.md)
2. Unable to reload entries in service (homeassistant.reload_config_entry).

<hr>
<br>


## Contribution

- ExpTech Studio `HTTP API`
- watermelon1024 `Python Function`
- kukuxx `Test Partner`

<p>I would like to thank everyone who has helped me and every partner in the community for their generous help.</p>

<hr>
<br>


## Future

- [ ] HomeAssistant Features: Integration loading its platforms from its own set up.
- [ ] HomeAssistant Features: Earthquake early warning by tracker device or person.
- [ ] HomeAssistant Service: Earthquake Simulator.
- [ ] HomeAssistant Service: Earthquake Sensor reload.
- [ ] ExptechTW Features: Earthquake early warning Source from WebSocket.
- [ ] ExptechTW Features: Exptech Subscribe (Ex: TREM-Net Earthquake early warning listener).

<hr>
<br>


> [!IMPORTANT]
>The source of earthquake early warning is provided by ExpTech Studio and is for reference only.<br>
>The actual results are subject to the content published by [CWA](https://scweb.cwa.gov.tw/en-US).

<hr>
<br>


## Donate

| Buy me a coffee | LINE Bank | JKao Pay |
| :------------: | :------------: | :------------: |
| <img src="https://github.com/J1A-T13N/ha-trem/assets/29163857/e61afedc-1fce-47a1-a6c3-00bc1a9a5329" alt="Buy me a coffee" height="200" width="200">  | <img src="https://github.com/J1A-T13N/ha-trem/assets/29163857/a0af96ea-7e03-47de-83ae-3c11b2e27c57" alt="Line Bank" height="200" width="200">  | <img src="https://github.com/J1A-T13N/ha-trem/assets/29163857/333def56-cf08-4f8e-a188-9067cc4f63d9" alt="JKo Pay" height="200" width="200">  |

<hr>
<br>


## License
AGPL-3.0 license


[black]: https://github.com/psf/black
[black-shield]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
[buymecoffee]: https://www.buymeacoffee.com/j1at13n
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/J1A-T13N/ha-trem.svg?style=for-the-badge
[commits]: https://github.com/J1A-T13N/ha-trem/commits/main
[hacs_custom]: https://hacs.xyz/docs/faq/custom_repositories
[hacs_custom_shield]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/J1A-T13N/ha-trem.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40jiatien-blue.svg?style=for-the-badge
[maintenance2-shield]: https://img.shields.io/badge/maintainer-%40watermelon-orange.svg?style=for-the-badge
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/J1A-T13N/ha-trem.svg?style=for-the-badge
[releases]: https://github.com/J1A-T13N/ha-trem/releases
[user_profile]: https://github.com/J1A-T13N
[user2_profile]: https://github.com/watermelon1024
