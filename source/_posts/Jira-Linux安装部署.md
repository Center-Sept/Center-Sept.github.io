---
title: Jira Linux安装部署
date: 2022-05-24 00:00:00
tags:
  - JIRA-Centos7
categories: []
---
# <a href="#Jira-Linux安装部署" class="headerlink" title="Jira Linux安装部署"></a>Jira Linux安装部署

## <a href="#1-下载安装" class="headerlink" title="1.下载安装"></a>1.下载安装

```shell
# 
yum install -y wget
# 
wget  https://downloads.atlassian.com/software/jira/downloads/atlassian-jira-software-7.3.6-x64.bin
# 
chmod 755 atlassian-jira-software-7.3.6-x64.bin
# 
./atlassian-jira-software-7.3.6-x64.bin
#
#
```

## <a href="#2-破解Jira，下载mysql驱动包用于配置连接数据库" class="headerlink" title="2.破解Jira，下载mysql驱动包用于配置连接数据库"></a>2.破解Jira，下载mysql驱动包用于配置连接数据库

```
# 进入默认安装目录：/opt/atlassian/jira ;
# 在网上寻找破解包和驱动包下载，进入安装目录下的./atlassian-jira/WEB-INF/lib/下,将准备好了的两个jar包上传到该目录下;(破解包需要替换,mysql驱动包不需要替换)
# 最后再进去安装目录下的./bin目录，./start-jira.sh 启动，./stop-jira.sh 停止; (其实使用的就是tomcat服务器,了解tomcat服务器目录结构很好理解)
# 最后使用你当前服务器的ip:port进入jira初始化界面;
```

## <a href="#3-配置初始化Jira" class="headerlink" title="3.配置初始化Jira"></a>3.配置初始化Jira

```
# 选择自己配置
# 然后选择其他数据库,根据使用的数据库选择数据类型,填写数据库参数,点击测试连接,弹出连接成功;
# 如果没问题就点击下一步,Jira会初始化数据库脚本（就是会创建表和初始化数据）
# 根据需求填写Jira管理方式以及基本URL
# 下一步许可证认证，这一步他会随机生成一个server ID，点击生成Jira使用许可证,进去官网注册账号，进去Licenses页面中生成许可证,然后复制临时许可证的key到刚刚的配置页面点击下一步；
# 最后配置管理员信息；
```

## <a href="#4-Jira基本的配置以及操作" class="headerlink" title="4.Jira基本的配置以及操作"></a>4.Jira基本的配置以及操作

```shell
# 
tail -f /opt/atlassian/jira/logs/catalina.out

# 
vim /opt/atlassian/jira/bin/setenv.sh

# 
/var/atlassian/application-data/jira/dbconfig.xml

# 
/opt/atlassian/jira/conf/server.xml
```

- [\#JIRA\|Centos7](/tags/JIRA-Centos7/)
