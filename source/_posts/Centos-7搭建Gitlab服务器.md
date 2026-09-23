---
title: "Centos 7搭建Gitlab服务器"
date: 2022-10-24 00:00:00
tags:
  - "gitlab|centos7"
categories:
  - "运维"  # 分类为 2026-09 回抄后新加，原文无
description: "Centos 7搭建Gitlab服务器 · 安装必要依赖 · 安装Postfix以发送通知邮件 · postfix服务设置成开机自启动 · 启动postfix · 下载rpm安装包 · 安装 · 修改配置文件vi /etc/gitlab/g…"
---
# Centos 7搭建Gitlab服务器

```shell
# 安装必要依赖
yum install policycoreutils-python
# 安装Postfix以发送通知邮件
yum install postfix
# postfix服务设置成开机自启动
systemctl enable postfix
# 启动postfix
systemctl start postfix
# 下载rpm安装包
wget https://mirrors.tuna.tsinghua.edu.cn/gitlab-ce/yum/el7/gitlab-ce-15.2.0-ce.0.el7.x86_64.rpm --no-check-certificate

# 安装
yum -y install gitlab-ce-15.2.0-ce.0.el7.x86_64.rpm
# 修改配置文件vi /etc/gitlab/gitlab.rb
# 修改如下配置，可以非本机访问
external_url 'http://192.168.40.129:8081'
# 对gitlab进行初始化
gitlab-ctl reconfigure
# 启动gitlab
gitlab-ctl restart
```

# GitLab的数据迁移

```shell
# 查看新旧服务器上安装的 gitlab 版本
# 注意：在迁移 gitlab 数据前首先要确保新旧服务器上安装的 gitlab 版本是一致的。
cat /opt/gitlab/embedded/service/gitlab-rails/VERSION

# 如果新旧服务器上安装的版本不一致
#例如： 旧服务器上GitLab版本10.3.3，新服务器上GitLab版本12.0.1。

#GitLab不能跨版本升级，需一个一个大版本升级。例如：10.8.7是10的最后一个版本，11.11.0是11的最后一个版本，则从 10.3.3 升级到 12.0.1，需要经过 10.3.3 -> 10.8.7 -> 11.11.0 -> 12.0.1三次版本升级。

#所以，要先在旧服务器上执行以下版本升级命令：
yum install -y gitlab-ce-10.8.7-ce.0.el7
yum install -y gitlab-ce-11.11.0-ce.0.el7
yum install -y gitlab-ce-12.0.1-ce.0.el7

#注：如果不指定版本号，则自动升级到最新版本。
yum install -y gitlab-ce  

# 先在旧服务器做gitlab数据备份文件
gitlab-rake gitlab:backup:create
#默认将会在 /var/opt/gitlab/backups/ 目录下生成备份文件

# 上传刚刚的备份文件到新服务器上
scp -Pxx 1615432132_2021_03_11_10.0.0_gitlab_backup.tar  root@xx.xx.xx.xx: /var/opt/gitlab/backups/

# 停止新服务器上gitlab数据连接服务
gitlab-ctl stop unicorn
gitlab-ctl stop sidekiq
# 恢复备份文件到GitLab
gitlab-rake gitlab:backup:restore BACKUP=备份文件编号
gitlab-rake gitlab:backup:restore BACKUP=1615432132_2021_03_11_10.0.0
# 重新启动GitLab
gitlab-ctl restart
```

# 配置gitlab服务器邮箱

```shell
# 编辑配置文件 
vim /etc/gitlab/gitlab.rb
# 配置如下：
gitlab_rails['smtp_enable'] = true
gitlab_rails['smtp_address'] = "smtp.163.com"
gitlab_rails['smtp_port'] = 25 # 网易端口为25
gitlab_rails['smtp_user_name'] = "xxxxx@163.com"
gitlab_rails['smtp_password'] = "" # POP3/SMTP/IMAP服务授权密码
gitlab_rails['smtp_domain'] = "163.com"
gitlab_rails['smtp_authentication'] = "login"
gitlab_rails['smtp_enable_starttls_auto'] = true
gitlab_rails['smtp_tls'] = false

### Email Settings
gitlab_rails['gitlab_email_enabled'] = true
gitlab_rails['gitlab_email_display_name'] = 'git server'  # 显示名字
gitlab_rails['gitlab_email_from'] = "xxxxx@163.com" # 发件邮箱
user["git_user_email"] = "xxxxx@163.com"

# 以下配置信息为访问配置
external_url 'http://localhost' # 真实IP或域名，无须添加端口号
gitlab_rails['host'] = 'localhost' # 真实IP或域名
gitlab_rails['port'] = 6080 # 映射80端口的主机(宿主)端口
gitlab_rails['gitlab_ssh_host'] = 'localhost' # 真实IP或域名
gitlab_rails['gitlab_shell_ssh_host'] = 6022 # 映射22端口的主机(宿主)端口
# ====================================================================
# 重新配置
gitlab-ctl reconfigure
# 实时查看所有执行日志
gitlab-ctl tail
# 测试邮件服务是否正常
gitlab-rails console

# irb(main):001:0>
# Notify.test_email(‘接收方地址’,‘邮件标题’,‘邮件内容’).deliver_now
Notify.test_email('xxxxxxxxxxx@qq.com','hello','hello').deliver_now

```
