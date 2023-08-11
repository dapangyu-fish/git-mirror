# git-mirror
# 超轻量github缓存镜像站(也支持其他git仓库,huggingface、gitlab...)
主要解决内网github依赖加速问题

## 使用说明
- docker-compose设置仓库本地存储路径，gitshark和nginx(lfs下载需要)都需要，路径相同即可
- 设置环境变量DOMAIN_NAME="192.168.111.225:3000" # 必须使用外部可访问的地址域名或ip:port, 这个是lfs对象的下载地址 8001是git的
- docker-compose up -d
- git clone http://192.168.111.225:8001/github.com/xxxx/xxxx.git
- 可自动缓存github项目,首次拉取仓库去取决于镜像服务->github网络速度及内网速度。

## 测试地址（公益）
- git clone https://home.dapangyu.work:8002/github.com/Genymobile/scrcpy.git
- 初次缓存的仓库会比较慢
## 进度

### 基础功能
- [x] git协议的http实现
  - [x] 无需上传因此阉割掉上传功能
  - [x] git二进制数据格式存疑,有些repo是压缩格式,先try解压except直接读
- [ ] git协议的ssh实现
- [x] 支持lfs
  - [x] 无需上传因此阉割掉上传功能  
  - [x] 文件服务器由nginx实现
- [x] redis缓存每个仓库的状态
  - [x] 记录每个仓库实时读区量
  - [x] 读取和更新仓库相互加锁
- [ ] 更新裸库
  - [x] 实现自动更新repo/lfs/refs并自动gc和repack
  - [ ] 更加高级的更新策略
  - [ ] api控制更新

### 其他功能
- [x] docker支持
- [x] arm64/aarch64平台支持
- [ ] 仓库分片支持

## 已知问题
- 目前仓库直接读取到内存，可能会比较耗内存，尚未大量测试
- python性能问题，流式响应flask比fastapi快20倍以上，原因未细究，flask依旧无法跑满带宽


## 虽然没什么大用但是 学习学习git协议～～

## Thanks

本项目主要参考[gitserver][1]，并对该项目表示感谢，除此之外还利用了类chatgpt的工具

- [gitserver][1]

[1]: https://github.com/meyer1994/gitserver