<h1 align="center">Taiwan Real-time Earthquake Monitoring for HA</h1>

![Logo](https://raw.githubusercontent.com/J1A-T13N/ha-trem/main/docs/media/logo.png)

[![License][license-shield]](LICENSE)
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![GitHub Release][releases-shield]][releases]
[![hacs_custom][hacs_custom_shield]][hacs_custom]

[![Project Maintenance][maintenance-shield]][user_profile]
[![Project Maintenance][maintenance2-shield]][user2_profile]
<hr>

[English](README.md) | 繁體中文<br>


## 預覽

![config_flow_image](https://github.com/J1A-T13N/ha-trem/assets/29163857/a6f4cc49-0521-4f27-a894-9fb1273be1cf)
![simulator_earthquake_demo](https://github.com/J1A-T13N/ha-trem/assets/29163857/b62dab7a-2935-4477-8297-f7e275df0a81)

<hr>
<br>


## 測試結果

| 環境 | Home Assistant OS | Home Assistant Core | Home Assistant Supervisor |
| :------------: | :------------: | :------------: | :------------: |
| Virtual Machine[^1] | :heavy_check_mark: |  |  |
| Container |  | :heavy_check_mark: | :question:[^2] |
| Virtual Environment |  | :heavy_check_mark: |  |
| Physics Machine[^3] | :question:[^4] | :heavy_minus_sign:[^5] | :question:[^2] |

:heavy_check_mark: 測試通過<br>
:heavy_multiplication_x: 無法安裝<br>
:question: 尚未測試<br>
:heavy_minus_sign: 請看備註<br>
[^1]: 虛擬機包括但不限: VirtualBox、Unraid、KVM/Proxmox、UTM...等。
[^2]: 如果您是按照[該方式](https://github.com/home-assistant/supervised-installer)安裝。
[^3]: 實體機包括但不限: Raspberry Pi、Home Assistant Green、Home Assistant Yellow...等。
[^4]: 到目前為止, 僅 rpi4 4GB 通過測試。
[^5]: 如果你有其他安裝環境, 可以協助測試並提供回饋。

<hr>
<br>


## 先決條件 (如果您使用的是 HAOS)
**請閱讀[指南](docs/haos_guide.md)來安裝必要套件.**

> [!IMPORTANT]
> 這個自訂元件安裝方法較為困難<br>
> 適合管理 Linux 系統專家才能安裝

> Home Assistant OS 暫存(tmp)目錄被掛載 noexec 導致無法編譯, 我們已找到 [解決辦法](https://github.com/home-assistant/core/issues/118717) 修復該問題。

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
**請跟隨設定流程新增.**

<hr>
<br>


## API 節點

| Node               | Description      |
| :----------------: | :--------------: |
| tainan_cache_limit | 請求次數遭到限制　 |
| tainan_cache       | 適合所有使用者　　 |
| taipe_cache_limit  | 請求次數遭到限制　 |
| taipe_cache        | 適合所有使用者　　 |
| taipei_limit       | 請求次數遭到限制　 |
| taipei             | 即時資料，但延遲高 |
| taipei_2           | 即時資料，但延遲高 |
| pingtung_limit     | 請求次數遭到限制　 |
| pingtung           | 即時資料，但延遲高 |
| pingtung_2         | 即時資料，但延遲高 |

*An API server can be monitored [here](https://status.exptech.dev/).*<br>


## 已知問題

> :tada: 暫時沒有發現問題

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

- [x] Integration 相關: Convert components from sensor to platform.
- [x] Integration 功能: 新增等震圖.
- [ ] ~~Integration 功能: 使用者位置或裝置追蹤計算預計震度即抵達時間.~~
- [x] Integration 功能: 模擬地震 (用於測試自動化)。
- [x] Integration 服務: 另存等震圖.
- [x] Integration 服務: 重新載入整合.
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
