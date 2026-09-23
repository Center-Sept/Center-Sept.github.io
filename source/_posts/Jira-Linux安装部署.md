---
title: "Jira Linux安装部署"
date: 2022-05-24 00:00:00
tags:
  - "JIRA|Centos7"
categories:
  - "运维"  # 分类为 2026-09 回抄后新加，原文无
description: "Jira Linux安装部署 · 1.下载安装 · 安装wget · 使用wget 下载jira安装包 · 给安装包赋权 · 执行安装程序 · 根据安装英文提示，做出自定义安装还是使用默认配置安装（略） · 注意安装文字提示的安装目录，便于…"
---
# Jira Linux安装部署

## 1.下载安装

```shell
# 安装wget
yum install -y wget
# 使用wget 下载jira安装包
wget  https://downloads.atlassian.com/software/jira/downloads/atlassian-jira-software-7.3.6-x64.bin
# 给安装包赋权
chmod 755 atlassian-jira-software-7.3.6-x64.bin
# 执行安装程序
./atlassian-jira-software-7.3.6-x64.bin
### 根据安装英文提示，做出自定义安装还是使用默认配置安装（略）
### 注意安装文字提示的安装目录，便于后面修改jira中的运行时配置以及数据库配置
```

## 2.破解Jira，下载mysql驱动包用于配置连接数据库

```plaintext
# 进入默认安装目录：/opt/atlassian/jira ;
# 在网上寻找破解包和驱动包下载，进入安装目录下的./atlassian-jira/WEB-INF/lib/下,将准备好了的两个jar包上传到该目录下;(破解包需要替换,mysql驱动包不需要替换)
# 最后再进去安装目录下的./bin目录，./start-jira.sh 启动，./stop-jira.sh 停止; (其实使用的就是tomcat服务器,了解tomcat服务器目录结构很好理解)
# 最后使用你当前服务器的ip:port进入jira初始化界面;
```

## 3.配置初始化Jira

```plaintext
# 选择自己配置
# 然后选择其他数据库,根据使用的数据库选择数据类型,填写数据库参数,点击测试连接,弹出连接成功;
# 如果没问题就点击下一步,Jira会初始化数据库脚本（就是会创建表和初始化数据）
# 根据需求填写Jira管理方式以及基本URL
# 下一步许可证认证，这一步他会随机生成一个server ID，点击生成Jira使用许可证,进去官网注册账号，进去Licenses页面中生成许可证,然后复制临时许可证的key到刚刚的配置页面点击下一步；
# 最后配置管理员信息；
```

## 4.Jira基本的配置以及操作

```shell
# 日志查看：
tail -f /opt/atlassian/jira/logs/catalina.out

# 如何修改内存？
vim /opt/atlassian/jira/bin/setenv.sh

# 连接数据库的配置
/var/atlassian/application-data/jira/dbconfig.xml

# 服务器配置文件
/opt/atlassian/jira/conf/server.xml
```
