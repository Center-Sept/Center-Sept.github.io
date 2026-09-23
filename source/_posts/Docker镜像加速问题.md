---
title: "Docker镜像加速问题"
date: 2023-03-27 00:00:00
tags:
  - "Docker"
categories:
  - "运维"  # 分类为 2026-09 回抄后新加，原文无
description: "出现问题 · 解决方法 · 编辑 /etc/docker/daemon.json · 增加如下文本 · 重载配置项 · 重启docker服务"
---
## 出现问题

```shell
Error response from daemon: Get "https://registry-1.docker.io/v2/": net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)
```

## 解决方法

```bash
# 编辑 /etc/docker/daemon.json
vi /etc/docker/daemon.json
# 增加如下文本
{"registry-mirrors":["https://reg-mirror.qiniu.com/","https://5wdlar25.mirror.aliyuncs.com","https://hub-mirror.c.163.com/","https://docker.mirrors.ustc.edu.cn/"]}
# 重载配置项
systemctl daemon-reload
# 重启docker服务
systemctl restart docker
```
