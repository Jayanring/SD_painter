1. 获取绘图参数包

    `git clone https://github.com/Jayanring/SD_painter.git`
    `cd SD_painter`
2. 创建outputs目录

    `mkdir outputs`
3. 填写配置

    `cp .env_template .env`
    
    `vim .env`
4. 运行容器

    调试：`docker run -it --rm -v ./.env:/sd/.env  -v ./args:/sd/args -v ./outputs:/sd/outputs --name sd_painter jayanring/sd_painter /bin/bash`
    
    运行：`docker run -d -v ./.env:/sd/.env  -v ./args:/sd/args -v ./outputs:/sd/outputs --name sd_painter jayanring/sd_painter`

    如果sd-webui运行在宿主机，还需要添加：
    `--add-host=host.docker.internal:host-gateway`

    使用`host.docker.internal`表示主机IP地址

    调试：`docker run -it --rm --add-host=host.docker.internal:host-gateway -v ./.env:/sd/.env  -v ./args:/sd/args -v ./outputs:/sd/outputs --name sd_painter jayanring/sd_painter /bin/bash`

    运行：`docker run -d --add-host=host.docker.internal:host-gateway -v ./.env:/sd/.env  -v ./args:/sd/args -v ./outputs:/sd/outputs --name sd_painter jayanring/sd_painter`