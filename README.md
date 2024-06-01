<h1 align="center">ha-trem</h1>
<h4 align="center">Taiwan Real-time Earthquake Monitoring for Home Assistant</h4>

<p align="center">
    <a href="https://github.com/J1A-T13N/ha-trem/pulls" target="_blank">
    <img src="https://img.shields.io/github/issues-pr-raw/J1A-T13N/ha-trem.svg?style=flat-square&logo=github&logoColor=white"
         alt="GitHub Pull Requests">
    </a>
    <a href="https://github.com/J1A-T13N/ha-trem/releases" target="_blank">
    <img src="https://img.shields.io/github/stars/J1A-T13N/ha-trem?style=flat-square"
         alt="GitHub Stars">
    </a>
    <a href="https://github.com/J1A-T13N/ha-trem/releases" target="_blank">
    <img src="https://img.shields.io/github/v/release/J1A-T13N/ha-trem.svg?style=flat-square&logo=github&logoColor=white"
         alt="Current version">
    </a>
</p>
<hr>
<br>


## Screenshots

![image](https://github.com/J1A-T13N/ha-trem/assets/29163857/620d2723-1d77-4ead-a203-6d0d612031fd)

<hr>
<br>


## Installation
### Using [HACS](https://hacs.xyz/) (recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=J1A-T13N&repository=ha-trem&category=Integration)

### Manual

1. Create `config/custom_components` folder if not existing.
2. Copy `trem` into `custom_components` folder.
3. Configure your name and region, in `config/configuration.yaml`.
4. Restart Home Assistant.

*An example of `configuration.yaml` can be found [here](configuration.yaml).*

#### Configuration

Add the following to your configuration.yaml file:
```yaml
sensor:
  - platform: trem
    name: Company # Display name
    region: 116 # Region Code (Zip Code)
  - platform: trem
    name: Sweet Home # Display name
    region: 231 # Region Code (Zip Code)
```

See [Region Code](https://raw.githubusercontent.com/ExpTechTW/TREM-tauri/main/src/assets/json/region.json).
<hr>
<br>


## Contribution

- ExpTech Studio `HTTP API`
- watermelon1024 `Python Function`
- kukuxx `Collaborator`

<p>在此感謝每一位幫助過我，及社群上的每一位夥伴，不吝給予協助。</p>
<hr>
<br>


## Future

- [ ] HomeAssistant Features: Integration loading its platforms from its own set up.
- [ ] HomeAssistant Features: Earthquake early warning by tracker device or person.
- [ ] HomeAssistant Service: Earthquake Simulator.
- [ ] HomeAssistant Service: Earthquake Sensor reload.
- [ ] ExptechTW Features: Earthquake early warning Source from WebSocket.
- [ ] ExptechTW Features: Exptech Subscribe (Ex: TREM-Net Earthquake early warning listener).

<br>
<hr>


<table>
<tr>
<td>
<br>
<p align="center">⚠️ Warning ⚠️</p>
示警資料來源由 ExpTech Studio 提供，僅供參考，<br>
實際結果依 中央氣象局 公佈之內容為準。
<br>
</td>
</tr>
</table>


## Donate

| Buy me a coffee | LINE Bank | JKao Pay |
| :------------: | :------------: | :------------: |
| <img src="https://github.com/J1A-T13N/ha-trem/assets/29163857/e61afedc-1fce-47a1-a6c3-00bc1a9a5329" alt="Buy me a coffee" height="200" width="200">  | <img src="https://github.com/J1A-T13N/ha-trem/assets/29163857/a0af96ea-7e03-47de-83ae-3c11b2e27c57" alt="Line Bank" height="200" width="200">  | <img src="https://github.com/J1A-T13N/ha-trem/assets/29163857/333def56-cf08-4f8e-a188-9067cc4f63d9" alt="JKo Pay" height="200" width="200">  |

<hr>
<br>


## Known issues

1. Unable to reload entries in service (homeassistant.reload_config_entry)

<hr>
<br>


## License
AGPL-3.0 license
