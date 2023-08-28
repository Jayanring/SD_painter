1. 获取绘图参数包

    `git clone https://github.com/Jayanring/SD_painter.git`
2. 创建outputs目录

    `mkdir outputs`
3. 填写配置

    `cp .env_template .env`
4. 运行容器

    `docker run -d -v ./.env:/sd/.env  -v ./args:/sd/args -v ./outputs:/sd/outputs --name sd_painter jayanring/sd_painter`
