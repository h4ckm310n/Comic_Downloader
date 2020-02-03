# Comic_Downloader

在线漫画下载器，大一时边学习Python边做出来的玩意儿（其实高二那会儿就有一个简单的命令行雏形了），当时只适配了dmzj。最近又捡回来继续做了，适配了更多的网站，在架构上也有所调整，完善了一些功能。这个项目是在Mac开发的，Windows环境还没测试过。


#### 界面：

![avatar](https://github.com/pwxssj/Comic_Downloader/blob/master/screenshots/search.png)

![avatar](https://github.com/pwxssj/Comic_Downloader/blob/master/screenshots/info.png)

![avatar](https://github.com/pwxssj/Comic_Downloader/blob/master/screenshots/dl.png)


#### 特性：

* 支持多个网站

* 多进程并发下载，可以设置进程数量（在config.json中修改）

* 可以选择是否在某个网站搜索（在config.json中修改）

* 下载完后可以生成cbz和pdf格式的漫画


#### 目前有待改善的问题：

* 没有异常处理机制

* 下载任务的暂停、恢复、删除可能存在一些bug


#### 接下来的计划：

* 适配更多网站

* 完善下载任务的管理

  
#### 目前支持的网站:

*	dmzj.com

* mangabz.com

* readcomicsonline.ru （英文）


#### 需要用到的库

* PyQt5

* requests

* cfscrape

* aiohttp

* asyncio

* json

* lxml

* urllib3

* PyExecJS

* Pillow

* multiprocessing

* importlib
