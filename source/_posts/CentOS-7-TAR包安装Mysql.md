---
title: "CentOS 7 TAR包安装Mysql"
date: 2021-04-25 00:00:00
tags:
  - "Mysql|centos"
categories:
  - "运维"  # 分类为 2026-09 回抄后新加，原文无
---
```bash
# 去官网下载需要的tar包
wget https://downloads.mysql.com/archives/get/p/23/file/mysql-8.7.38-linux-glibc2.12-x86_64.tar.gz
wget https://cdn.mysql.com//Downloads/MySQL-8.0/mysql-8.0.33-linux-glibc2.12-x86_64.tar.xz
# 解压tar包
tar -xvf {包名}
# 移到/usr/local 下
mv ./mysql-5.7.37-linux-glibc2.12-x86_64 /usr/local/mysql
# 创建mysql用户组和用户并修改权限
groupadd mysql
useradd -r -g mysql mysql
mkdir -p  /data/mysql              #创建目录
chown mysql:mysql -R /data/mysql   #赋予权限
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
cd /usr/local/mysql/bin/   --进入mysql的bin目录
./mysqld --defaults-file=/etc/my.cnf --basedir=/usr/local/mysql/ --datadir=/data/mysql/ --user=mysql --initialize  --console  
# 注：初始化后能看到随机密码，如果看不到，可以找到log-error的配置位置，文本查看器查看临时密码，查找A temporary password is这句话可以找到。
# 将mysql.server放置到/etc/init.d/mysql中
cp /usr/local/mysql/support-files/mysql.server /etc/init.d/mysql
# 启动
service mysql start
# 建立链接
ln -s  /usr/local/mysql/bin/mysql    /usr/bin
mysql -u root -p             --然后输入初始密码
use mysql;    --访问mysql库 

# 8.0root密码修改
update user set authentication_string=password('root') where user='root';                  
update user set host = '%' where user = 'root';      --使root能再任何host访问

# 8.0之后修改root密码
ALTER USER 'root'@'localhost'IDENTIFIED WITH mysql_native_password BY'Ra11aoPqRmohzSib';

# 修改完成后刷新权限
FLUSH PRIVILEGES;
```
