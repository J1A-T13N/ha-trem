## Fix the problem that the dependencies cannot be installed

> [!IMPORTANT]
> This custom component installation is considered advanced<br>
> should only be used if one is an expert in managing a Linux operating system.

> [!IMPORTANT]
> Minimum system requirements your device must meet to install dependencies: <br>
> RAM: 4GB, If your device has less than 4GB of memory, A memory error may have occurred.
> Storage: 64 GB or larger storage device.

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
7. Copy and paste into the Terminal to install the dependencies
```bash
apk add e2fsprogs musl-dev gdal-dev proj-dev proj-util gcc g++ gfortran openblas-dev linux-headers
fallocate -l 4G /usr/tmp-disk
mkfs.ext4 /usr/tmp-disk
mount -o loop -t ext4 /usr/tmp-disk /tmp
pip install --no-cache-dir pandas==2.1.4 geopandas==0.14.4 matplotlib==3.9.0 scipy==1.12.0 obspy==1.4.0
```

![image](https://github.com/J1A-T13N/ha-trem/assets/29163857/b207f304-65bd-4ed2-aefb-60caf51f412c)
8. If everything is successfully, [Continue configuration the integration](../README.md#config).

> [!NOTE]
> Excessive memory use when install Matplotlib [^1], A [workaround](https://stackoverflow.com/questions/29466663/memory-error-while-using-pip-install-matplotlib) is to run pip with `--no-cache-dir` to avoid the cache.
[^1]: This error is coming up because, it seems, pip's caching mechanism is trying to read the entire file into memory before caching it… which poses a problem in a limited-memory environment, as matplotlib is ~50mb.
<hr>
<br>


### Docker Terminal
1. Open a terminal and login
2. Go inside the container with docker exec -it homeassistant bash (or similar)
3. Copy and paste into the Terminal to install the dependencies
```bash
apk add e2fsprogs musl-dev gdal-dev proj-dev proj-util gcc g++ gfortran openblas-dev linux-headers
fallocate -l 4G /usr/tmp-disk
mkfs.ext4 /usr/tmp-disk
mount -o loop -t ext4 /usr/tmp-disk /tmp
pip install --no-cache-dir pandas==2.1.4 geopandas==0.14.4 matplotlib==3.9.0 scipy==1.12.0 obspy==1.4.0
```

4. If everything is successfully, [Continue configuration the integration](../README.md#config).

> [!NOTE]
> Excessive memory use when install Matplotlib [^1], A [workaround](https://stackoverflow.com/questions/29466663/memory-error-while-using-pip-install-matplotlib) is to run pip with `--no-cache-dir` to avoid the cache.
[^1]: This error is coming up because, it seems, pip's caching mechanism is trying to read the entire file into memory before caching it… which poses a problem in a limited-memory environment, as matplotlib is ~50mb.
<hr>
<br>
