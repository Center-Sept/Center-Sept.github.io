---
title: CentOS 7 TAR包安装Mysql
date: 2021-04-25 00:00:00
tags:
  - Mysql-centos
categories: []
---
```bash
# 去官网下载需要的tar包
wget https://downloads.mysql.com/archives/get/p/23/file/mysql-8.7.38-linux-glibc2.12-x86_64.tar.gz
wget https://cdn.mysql.com//Downloads/MySQL-8.0/mysql-8.0.33-linux-glibc2.12-x86_64.tar.xz
# 解压tar包
tar -xvf {包名}
# 移到/usr/local 下
mv
# 创建mysql用户组和用户并修改权限
groupadd mysql
useradd -r -g mysql mysql
mkdir
chown
# 配置my.cnf
[mysqld]
bind-address=0.0.0.0
port=3306
user=mysql
basedir=/usr/local/mysql      --重要
datadir=/data/mysql           --重要
socket=/tmp/mysql.sock
log-error=/data/mysql/mysql.err
pid-file=/data/mysql/mysql.pid
#character config
character_set_server=utf8mb4
symbolic-links=0
explicit_defaults_for_timestamp=true
# 初始化数据库
cd
./mysqld --defaults-file=/etc/my.cnf --basedir=/usr/local/mysql/ --datadir=/data/mysql/ --user=mysql --initialize  --console  
# 注：初始化后能看到随机密码，如果看不到，可以找到log-error的配置位置，文本查看器查看临时密码，查找A temporary password is这句话可以找到。
# 将mysql.server放置到/etc/init.d/mysql中
cp
# 启动
service mysql start
# 建立链接
ln
mysql -u root -p             --然后输入初始密码
use mysql;    --访问mysql库 

# 8.0root密码修改
update user set
update user set

# 8.0之后修改root密码
ALTER USER 'root'

# 修改完成后刷新权限
FLUSH PRIVILEGES;
```

- [\#Mysql\|centos](/tags/Mysql-centos/)
