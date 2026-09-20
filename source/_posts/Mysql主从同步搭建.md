---
title: Mysql主从同步搭建
date: 2022-04-25 00:00:00
tags:
  - Mysql-主从同步
categories: []
---
## <a href="#概念" class="headerlink" title="概念"></a>概念

### <a href="#主从同步的流程（原理）" class="headerlink" title="主从同步的流程（原理）"></a>主从同步的流程（原理）

- master 将变动记录到二进制日志文件（binary log）中，即配置文件中 log-bin 指定的文件，这些记录叫做二进制日志事件(binary log events)；
- master 将二进制日志文件发送给 slave；
- slave 通过 I/O 线程读取文件中的内容写到 relay 日志中；
- slave 执行 relay 日志中的事件，完成数据在本地的存储。

### <a href="#搭建主从需要注意的事项：" class="headerlink" title="搭建主从需要注意的事项："></a>搭建主从需要注意的事项：

- 主从服务器操作系统版本和位数一致；
- Master 和 Slave 数据库版本要一致；
- Master 和 Slave 数据库中的数据要一致；
- Master 开启二进制日志， Master 和 Slave 的 server_id 在局域网内必须唯一。

## <a href="#步骤" class="headerlink" title="步骤"></a>步骤

### <a href="#Master-上的操作" class="headerlink" title="Master 上的操作"></a>Master 上的操作

1.  修改 master 的配置（ my.cnf）加入下面的内容：

```
[mysqld]
log-bin=mysql-bin
# id必须唯一和从机区别开来
server-id=1
```

2.  重启mysql

```shell
systemctl restart mysql
```

3.  在 master 中创建用于主从同步的用户

```
# 创建用户
CREATE USER 'slave1'@'{从机内网ip地址}' IDENTIFIED WITH mysql_native_password BY 'slave1';
# 授权用户
GRANT REPLICATION SLAVE ON *.* TO 'slave1'@'{从机内网ip地址}';
# 刷新权限
FLUSH PRIVILEGES;
```

4.  查看主服务器状态

```
show master status;
```

记录下 File 和 Position 的值，之后要用到

### <a href="#Slave-上的操作" class="headerlink" title="Slave 上的操作"></a>Slave 上的操作

1.  修改slave 的配置（ my.cnf）加入下面的内容

```
[mysqld]
# id必须唯一和从机区别开来
server-id=2
```

2.  重启 slave

```shell
systemctl restart mysql
```

3.  登录 MySQL 并运行以下命令，设置主节点参数

```bash
mysql> CHANGE MASTER TO
MASTER_HOST='{master的内网IP地址}'
MASTER_USER='{创建的主从同步用户名:slave1}'
MASTER_PASSWORD='{创建的主从同步密码:slave1}'
MASTER_LOG_FILE='{show master status查看的File值:mysql-bin.000003}'
MASTER_LOG_POS={show master status查看的Position值:621};
```

4.  查看主从同步的状态

```
mysql> show slave status\G;
```

检查下面的信息，都为 yes 才代表搭建成功：

```
Slave_IO_Running: Yes
Slave_SQL_Running: Yes
```

- [\#Mysql\|主从同步](/tags/Mysql-%E4%B8%BB%E4%BB%8E%E5%90%8C%E6%AD%A5/)
