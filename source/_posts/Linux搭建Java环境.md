---
title: Linux搭建Java环境
date: 2021-04-25 00:00:00
tags:
  - Java-Linux
categories: []
---
1.  查看linux位数

查看linux是32位还是64位，影响需要下载JDK的版本

| 系统位数       | jdk位数   |
|:---------------|:----------|
| x86（32位）    | 32位      |
| x86_64（64位） | 32位 64位 |

在linux命令输入：

```
uname -a
```

如果是64位机器，会输出x86_64

2.  下载JDK

下载地址：<a href="https://download.oracle.com/otn/java/jdk/8u371-b11/ce59cff5c23f4e2eaf4e778a117d4c5b/jdk-8u371-linux-x64.tar.gz" class="link" target="_blank" rel="noopener">https://download.oracle.com/otn/java/jdk/8u371-b11/ce59cff5c23f4e2eaf4e778a117d4c5b/jdk-8u371-linux-x64.tar.gz<em></em></a>

3.  安装JDK

```bash
# 将下载的jdk上传到linux，解压压缩包文件
tar -xvf jdk-8u371-linux-x64.tar.gz
# 移动到/usr/local文件夹下
mkdir
# 编辑环境变量文件/etc/profile
vi /etc/profile
# 加入如下配置
#改成jdk的安装路径
export
export
export
# 使配置生效
source
# 测试结果
java -version
```

- [\#Java\|Linux](/tags/Java-Linux/)
