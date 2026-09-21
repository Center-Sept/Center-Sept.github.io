---
title: "MongoDB_7 Centos7部署"
date: 2023-09-11 00:00:00
tags:
  - "MongoDB | 安装&部署"
categories:
  - "运维"  # 分类为 2026-09 回抄后新加，原文无
---
# MongoDB_7 Centos7部署

## 1.环境准备

- 操作系统：Linux CentOS 7
- 安装包：mongodb-linux-x86_64-rhel70-7.0.2-rc1.tgz

## 2.软件启动安装

1.将下载好的安装包上传到 Linux 服务器某个目录下，并使用以下命令解压压缩包。

```shell
tar -zxvf mongodb-linux-x86_64-rhel70-7.0.2-rc1.tgz
```

2.将解压后的目录移动到 `/usr/local` 目录下，并改名为 `mongodb`

```shell
mv mongodb-linux-x86_64-rhel70-7.0.2-rc1 /usr/local/mongodb
```

3.进入 mongodb 目录，并创建文件夹 data，在 data 文件夹下再创建 db 文件夹（用于存放数据库数据）和 log文件夹（存放 mongo 日志）。然后为其设置可读写权限。

```shell
# 进入目录
cd /usr/local/mongodb/

# 创建三个文件夹
mkdir data data/db data/log

# 设置可读写权限
sudo chmod 777 data/db data/log/
```

4.在 mongodb 目录下新建配置文件 `mongodb.conf`（可选，但建议配置），打开文件输入以下内容。

```plaintext
# 数据库数据存放目录
dbpath=/usr/local/mongodb/data/db
# 日志文件存放目录
logpath=/usr/local/mongodb/data/log/mongodb.log
# 日志追加方式
logappend=true
# 端口
port=27017
# 是否认证
auth=true
# 以守护进程方式在后台运行
fork=true
# 远程连接要指定ip，否则无法连接；0.0.0.0代表不限制ip访问
bind_ip=0.0.0.0
```

5.配置环境变量，使用 `sudo vi /etc/profile` 命令打开系统文件，并在末尾加入以下内容后保存，最后使用 `source /etc/profile` 命令重启系统配置。

```plaintext
export MONGODB_HOME=/usr/local/mongodb
export PATH=$PATH:$MONGODB_HOME/bin
```

6.完成以上步骤即可启动 Mongo 服务。

```plaintext
# -f 等同于--config
mongod -f /usr/local/mongodb/mongodb.conf 
about to fork child process, waiting until server is ready for connections.
forked process: 1566
child process started successfully, parent exiting
```

7.安装客户端，安装mongdb shell工具。

```shell
# 下载安装包
wget https://fastdl.mongodb.org/linux/mongodb-shell-linux-x86_64-rhel70-3.6.23.tgz
# 解压
tar -zxvf mongodb-shell-linux-x86_64-rhel70-3.6.23.tgz
# 移动到统一文件夹下
mv mongodb-linux-x86_64-rhel70-3.6.23 /usr/local/mongodb-shell
# 配置环境变量
vi /etc/profile
# 如下：
# MongoDB-shell环境变量
export MONGODB_SHELL_HOME=/usr/local/mongodb-shell
export PATH=$PATH:$MONGODB_SHELL_HOME/bin
# 配置生效
source /etc/profile
# 测试连接
mongo
# 进入session说明成功
```

## 3.其他配置

### 1.开放端口

```shell
# 开放27017端口
firewall-cmd --zone=public --add-port=27017/tcp --permanent
# 让配置生效
firewall-cmd --reload
# 查看开放的端口，验证是否成功
firewall-cmd --zone=public --list-ports
#或者直接关闭防火墙
```

### 2.检查服务状态

```shell
# 查看 mongodb 进程状态
ps aux | grep mongo
# 检查端口是否启动
netstat -lanp | grep 27017
# 如果 netstat 命令没有找到，先进行安装
yum install -y net-tools
```

### 3.停止服务

```shell
# 通过进程ID杀死
kill -9 PID
# 通过mongod命令关闭mongodb服务
mongod -f /usr/local/mongodb/mongodb.conf  --shutdown
```

### 4.开机启动

使用 `vi /lib/systemd/system/mongodb.service` 命令新建开机启动配置文件，输入以下内容保存。

```plaintext
[Unit]
    Description=mongodb
    After=network.target remote-fs.target nss-lookup.target
[Service]
    Type=forking
    ExecStart=/usr/local/mongodb/bin/mongod -f /usr/local/mongodb/mongodb.conf
    ExecReload=/bin/kill -s HUP $MAINPID
    ExecStop=/usr/local/mongodb/bin/mongod -f /usr/local/mongodb/mongodb.conf --shutdown
    PrivateTmp=true
[Install]
    WantedBy=multi-user.target
```

然后依次执行以下4个命令，使之生效。

```shell
# 启动 mongodb
systemctl start mongodb.service
# 查看服务状态
systemctl status mongodb.service
# 开机自启动
systemctl enable mongodb.service
# 修改 mongodb.service文件时，重新加载文件
systemctl daemon-reload
```

## 4.用户角色和密码

启动 MongoDB 服务默认是没有账号密码的，即连接上即可进行各种操作。

但是我们在启动配置文件中，指定了 auth=true，即开启了认证，所以链接后需要认证才能执行操作。默认情况下，MongoDB 是没有管理员账户的，所以我们需要在 admin 数据库中使用 db.createUser() 命令添加管理员帐号或其他角色。

### 1.内置角色

数据库用户角色：read、readWrite  
数据库管理角色：dbAdmin、dbOwner、userAdmin  
集群管理角色：clusterAdmin、clusterManager、clusterMonitor、hostManager  
备份恢复角色：backup、restore  
所有数据库角色：readAnyDatabase、readWriteAnyDatabase、userAdminAnyDatabase、dbAdminAnyDatabase  
超级用户角色：root  
内部角色：\_\_system

### 2.创建管理员账号

```plaintext
> use admin
> db.createUser({ 
    user: "admin", 
    pwd: "admin", 
    roles: [ { role: "userAdminAnyDatabase", db: "admin" } ], 
    mechanisms : ["SCRAM-SHA-1"] 
})
```

### 3. 验证

```plaintext
> use admin
> db.auth("admin","admin")
> show tables
system.users
system.version
```

### 4.演示对单个数据库创建用户和密码

平常开发中，一般新项目会创建新的数据库，而且创建一个新的数据库用户仅对此数据库进行读写。

以下演示创建 chenpi 用户，密码为123456，并设置对 nobody 数据库读写的权限。注意，创建新用户前，先使用 admin 用户登录，因为我们刚才为 admin 用户设置了 userAdminAnyDatabase 权限。

```plaintext
# 先使用有创建用户权限的用户登录
> use admin
> db.auth("admin","123456")
# 新用户的认证库
> use test
# 创建chenpi用户，密码123465，对nobody数据库有读写权限
> db.createUser({user:'test',pwd:'test',roles:[{role:'readWrite',db:'nobody'}],mechanisms : ["SCRAM-SHA-1"]})
```

## 5.MongoDB可视化工具(Studio 3T For MongoDB)

\[Download Studio 3T for MongoDB \| Windows, macOS & Linux\](
