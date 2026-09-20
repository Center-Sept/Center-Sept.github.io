---
title: Centos 7搭建Gitlab服务器
date: 2022-10-24 00:00:00
tags:
  - gitlab-centos7
categories: []
---
# <a href="#Centos-7搭建Gitlab服务器" class="headerlink" title="Centos 7搭建Gitlab服务器"></a>Centos 7搭建Gitlab服务器

```shell
# 
yum install policycoreutils-python
# 
yum install postfix
# 
systemctl enable postfix
# 
systemctl start postfix
# 
wget https://mirrors.tuna.tsinghua.edu.cn/gitlab-ce/yum/el7/gitlab-ce-15.2.0-ce.0.el7.x86_64.rpm --no-check-certificate

# 
yum -y install gitlab-ce-15.2.0-ce.0.el7.x86_64.rpm
# 
# 
external_url 'http://192.168.40.129:8081'
# 
gitlab-ctl reconfigure
# 
gitlab-ctl restart
```

# <a href="#GitLab的数据迁移" class="headerlink" title="GitLab的数据迁移"></a>GitLab的数据迁移

```shell
# 
# 
cat /opt/gitlab/embedded/service/gitlab-rails/VERSION

# 
#

#

#
yum install -y gitlab-ce-10.8.7-ce.0.el7
yum install -y gitlab-ce-11.11.0-ce.0.el7
yum install -y gitlab-ce-12.0.1-ce.0.el7

#
yum install -y gitlab-ce  

# 
gitlab-rake gitlab:backup:create
#

# 
scp -Pxx 1615432132_2021_03_11_10.0.0_gitlab_backup.tar  root@xx.xx.xx.xx: /var/opt/gitlab/backups/

# 
gitlab-ctl stop unicorn
gitlab-ctl stop sidekiq
# 
gitlab-rake gitlab:backup:restore BACKUP=备份文件编号
gitlab-rake gitlab:backup:restore BACKUP=1615432132_2021_03_11_10.0.0
# 
gitlab-ctl restart
```

# <a href="#配置gitlab服务器邮箱" class="headerlink" title="配置gitlab服务器邮箱"></a>配置gitlab服务器邮箱

```shell
# 
vim /etc/gitlab/gitlab.rb
# 
gitlab_rails['smtp_enable'] = true
gitlab_rails['smtp_address'] = "smtp.163.com"
gitlab_rails['smtp_port'] = 25 # 网易端口为25
gitlab_rails['smtp_user_name'] = "xxxxx@163.com"
gitlab_rails['smtp_password'] = "" # POP3/SMTP/IMAP服务授权密码
gitlab_rails['smtp_domain'] = "163.com"
gitlab_rails['smtp_authentication'] = "login"
gitlab_rails['smtp_enable_starttls_auto'] = true
gitlab_rails['smtp_tls'] = false

#
gitlab_rails['gitlab_email_enabled'] = true
gitlab_rails['gitlab_email_display_name'] = 'git server'  # 显示名字
gitlab_rails['gitlab_email_from'] = "xxxxx@163.com" # 发件邮箱
user["git_user_email"] = "xxxxx@163.com"

# 
external_url 'http://localhost' # 真实IP或域名，无须添加端口号
gitlab_rails['host'] = 'localhost' # 真实IP或域名
gitlab_rails['port'] = 6080 # 映射80端口的主机(宿主)端口
gitlab_rails['gitlab_ssh_host'] = 'localhost' # 真实IP或域名
gitlab_rails['gitlab_shell_ssh_host'] = 6022 # 映射22端口的主机(宿主)端口
# 
# 
gitlab-ctl reconfigure
# 
gitlab-ctl tail
# 
gitlab-rails console

# 
# 
Notify.test_email('xxxxxxxxxxx@qq.com','hello','hello').deliver_now

```

- [\#gitlab\|centos7](/tags/gitlab-centos7/)
