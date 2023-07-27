# git-mirror
git miror with cache
# github缓存

## 进度

- [x] git协议的http实现
  - [x]  无需上传因此阉割掉上传功能
  - [x] git二进制数据格式存疑,有些repo是压缩格式,先try解压except直接读
- [x] 支持lfs
  - [x] 无需上传因此阉割掉上传功能  
  - [x] 文件服务器由nginx实现
- [ ] redis缓存每个仓库的状态
  - [x] 记录每个仓库实时读区量
  - [ ] 读取和更新仓库相互加锁
- [ ] 更新裸库
  - [x] 实现自动更新repo/lfs/refs并自动gc和repack
  - [ ] 更加高级的更新策略
  - [ ] api控制更新
- [] 仓库分片支持