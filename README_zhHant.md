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


[English](README.md) | 繁體中文<br>

> [!IMPORTANT]
> 這個自訂元件安裝方法較為困難<br>
> 適合管理 Linux 系統專家才能安裝


## 預覽

![image](https://github.com/J1A-T13N/ha-trem/assets/29163857/620d2723-1d77-4ead-a203-6d0d612031fd)

<hr>
<br>


## 測試結果

| 環境 | Home Assistant OS[^1] | Home Assistant Core | Home Assistant Supervisor |
| :------------: | :------------: | :------------: | :------------: |
| Virtual Machine[^2] | :heavy_check_mark: |  |  |
| Container |  | :heavy_check_mark: | :question:[^3] |
| Virtual Environment |  | :heavy_check_mark: |  |
| Physics Machine[^4] | :question:[^5] | :heavy_minus_sign:[^6] | :question:[^3] |

:heavy_check_mark: 測試通過<br>
:heavy_multiplication_x: 無法安裝<br>
:question: 尚未測試<br>
:heavy_minus_sign: 請看備註<br>
[^1]: Home Assistant OS 暫存(tmp)目錄被掛載 noexec 導致無法編譯, 您可以透過此 [解決辦法](https://github.com/home-assistant/core/issues/118717) 在容器內安裝所需套件。
[^2]: 虛擬機包括但不限: VirtualBox、Unraid、KVM/Proxmox、UTM...等。
[^3]: 如果您是按照[該方式](https://github.com/home-assistant/supervised-installer)安裝。
[^4]: 實體機包括但不限: Raspberry Pi、Home Assistant Green、Home Assistant Yellow...等。
[^5]: 到目前為止, 僅 Raspberry Pi 4 通過測試。
[^6]: 如果你有其他安裝環境, 可以協助測試並提供回饋。

<hr>
<br>


## 安裝方式

### 透過 [HACS](https://hacs.xyz/) (推薦)
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=J1A-T13N&repository=ha-trem&category=Integration)

### 手動安裝
1. 如果 `config/custom_components` 不存在，請建立該資料夾
2. 複製 `trem` 到 `custom_components` 資料夾內

<hr>
<br>


## 設定

```yaml
sensor:
  - platform: trem
    friendly_name: Company # 顯示名稱
    region: 116 # 示警地區
  - platform: trem
    friendly_name: Sweet Home # 顯示名稱
    region: 231 # 示警地區
    keep_alive: True # 保留示警記錄
```
> [!TIP]
> 此configuration適用v0.0.2以上版本<br>
> Release v0.0.1 請將`friendly_name`改回`name`。
<br>

**:zap: 請記得重啟 Home Assistant. :zap:**

<hr>
<br>


## 選項
| Name                  | Type             | Requirement  | Description                                                                                                                                                                                                                       | Default   |
| --------------------- | ---------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| region                | string           | **Required** | 示警地區代號可[在此處](https://github.com/ExpTechTW/TREM-tauri/blob/main/src/assets/json/region.json)查詢                                                                                                                             |           |
| friendly_name         | string           | **Optional** | 您想顯示的名稱                                                                                                                                                                                                                      | `Taiwan Real-time Earthquake Monitoring`      |
| keep_alive            | boolean          | **Optional** | 保留最近的示警資料                                                                                                                                                                                                                   | `false` |

*`configuration.yaml` 示範檔案可[在此處](configuration.yaml)查看。*<br>

<hr>
<br>


## 已知問題

1. 無法安裝必要套件問題已解決, 請查看[指南](docs/haos_guide.md)安裝。
2. 無法透過服務(homeassistant.reload_config_entry)重新載入。

<hr>
<br>


## 貢獻者

- ExpTech Studio 探索科技 `示警資料`
- watermelon1024 `計算程式`
- kukuxx `解決辦法提供者`

<p>在此感謝每一位幫助過我，及社群上的每一位夥伴，不吝給予協助。</p>
<hr>
<br>


## 未來功能

- [ ] HomeAssistant: 採用平台集合提供更多服務 (例如：等震圖繪製)。
- [ ] HomeAssistant: 地震速報以使用者或自訂定位，計算震度及抵達時間。
- [ ] HomeAssistant: 模擬地震服務 (用於測試自動化)。
- [ ] HomeAssistant: 透過服務(homeassistant.reload_config_entry)重新載入。
- [ ] ExptechTW 訂閱功能: 使用WebSocket作為地震速報來源，減少流量及延遲。
- [ ] ExptechTW 訂閱功能: 更多訂閱方案 (例如: TREM-Net地震速報網)。

<hr>
<br>


> [!IMPORTANT]
>示警資料來源由 ExpTech Studio 提供，僅供參考，<br>
>實際結果依 [中央氣象局](https://scweb.cwa.gov.tw/en-US) 公佈之內容為準。

<hr>
<br>


## 贊助

| Buy me a coffee | LINE Bank | JKao Pay |
| :------------: | :------------: | :------------: |
| <img src="https://github.com/J1A-T13N/ha-trem/assets/29163857/e61afedc-1fce-47a1-a6c3-00bc1a9a5329" alt="Buy me a coffee" height="200" width="200">  | <img src="https://github.com/J1A-T13N/ha-trem/assets/29163857/a0af96ea-7e03-47de-83ae-3c11b2e27c57" alt="Line Bank" height="200" width="200">  | <img src="https://github.com/J1A-T13N/ha-trem/assets/29163857/333def56-cf08-4f8e-a188-9067cc4f63d9" alt="JKo Pay" height="200" width="200">  |

<hr>
<br>


## 授權
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
