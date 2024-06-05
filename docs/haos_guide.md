## Fix the problem that the geopandas package cannot be installed

### SSH Add-on (Recommended)
1. Go to the Add-on store<br>
[![Open this add-on in your Home Assistant instance.](https://my.home-assistant.io/badges/supervisor_addon.svg)](https://my.home-assistant.io/redirect/supervisor_addon/?addon=a0d7b954_ssh&repository_url=https%3A%2F%2Fgithub.com%2Fhassio-addons%2Frepository)
2. Install one of the SSH add-ons (you need to enable advanced mode in your user profile to see [here](https://github.com/hassio-addons/addon-ssh/blob/main/ssh/DOCS.md#installation))
3. Configure the SSH add-on you chose by following the [documentation](https://github.com/hassio-addons/addon-ssh/blob/main/ssh/DOCS.md#configuration) for it
4. Sure disable protection mode and Start the SSH add-on
5. Connect to the SSH add-on
6. Copy and paste into the Terminal to enter Home Assistant CLI
```bash
login
docker exec -it homeassistant bash
```
![image](https://github.com/J1A-T13N/ha-trem/assets/29163857/36748f45-03c1-4f3e-814e-cd54167606b7)
7. Copy and paste into the Terminal to install the geopandas package
```bash
apk add --no-cache e2fsprogs musl-dev gdal-dev proj-dev proj-util gcc g++
fallocate -l 1G /usr/tmp-disk
mkfs.ext4 /usr/tmp-disk
mount -o loop -t ext4 /usr/tmp-disk /tmp
pip install geopandas==0.14.4 matplotlib==3.9.0
```
![image](https://github.com/J1A-T13N/ha-trem/assets/29163857/b207f304-65bd-4ed2-aefb-60caf51f412c)
8. If everything is successfully, [Continue configuration the integration](../README.md#config).

<hr>
<br>


### Docker Terminal
1. Open a terminal and login
2. Go inside the container with docker exec -it homeassistant bash (or similar)
3. Copy and paste into the Terminal.
```bash
apk add --no-cache e2fsprogs musl-dev gdal-dev proj-dev proj-util gcc g++
fallocate -l 1G /usr/tmp-disk
mkfs.ext4 /usr/tmp-disk
mount -o loop -t ext4 /usr/tmp-disk /tmp
pip install geopandas==0.14.4 matplotlib==3.9.0
```
4. If everything is successfully, [Continue configuration the integration](../README.md#config).

<hr>
<br>
  

### Service (Not recommended)
1. Add the following to your configuration.yaml file:
```yaml
shell_command:
  extlib_install: >
    apk add --no-cache e2fsprogs musl-dev gdal-dev proj-dev proj-util gcc g++
  trem_install: >
    pip install geopandas==0.14.4 matplotlib==3.9.0
```
2. Restart Home Assistant.
3. Go to Developer tools > Service in the sidebar
4. Click [GO TO YAML MODE], Copy and paste into the text box.
```yaml
service: shell_command.extlib_install
```
5. Click [CALL SERVICE] and wait for the response extension library to be installed success.
6. Copy and paste into the text box.
```yaml
service: shell_command.trem_install
```
7. Click [CALL SERVICE] and wait for the response required library to be installed success.
8. If everything is successfully, [Continue configuration the integration](../README.md#config).
