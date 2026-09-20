---
title: Docker快速搭建Zookeeper和kafka集群
date: 2021-07-24 00:00:00
tags:
  - docker-kafka-zookeeper
categories: []
---
# <a href="#安装" class="headerlink" title="安装"></a>安装

**前提：安装docker和docker-compose**

**镜像选择**

```
Zookeeper和Kafka集群分别运行在不同的容器中
zookeeper官方镜像，版本3.4 （zookeeper:3.4）
kafka采用wurstmeister/kafka镜像
kafka-manager采用sheepkiller/kafka-manager:latest镜像
```

**实现目标**

```
kafka集群在docker网络中可用，和zookeeper处于同一网络
宿主机可以访问zookeeper集群和kafka的broker list
docker重启时集群自动重启
集群的数据文件映射到宿主机器目录中
使用yml文件和$ docker-compose up -d命令创建或重建集群
```

**拉取镜像**

```
docker pull zookeeper:3.4
docker pull wurstmeister/kafka
docker pull sheepkiller/kafka-manager:latest
123
```

**创建集群网络**

```shell
docker network create --driver bridge --subnet 172.19.0.0/16 --gateway 172.19.0.1 kafka
```

**查看网络**

```shell
docker network ls
```

**zk集群的docker-compose.yml（任意目录下创建docker-compose.yml文件）**

```yml
version:

services:
  zoo1:
    image:
    restart:
    hostname:
    container_name:
    ports:
    -
    volumes:
    -
    -
    environment:
      ZOO_MY_ID:
      ZOO_SERVERS:
    networks:
      kafka:
        ipv4_address:

  zoo2:
    image:
    restart:
    hostname:
    container_name:
    ports:
    -
    volumes:
    -
    -
    environment:
      ZOO_MY_ID:
      ZOO_SERVERS:
    networks:
      kafka:
        ipv4_address:

  zoo3:
    image:
    restart:
    hostname:
    container_name:
    ports:
    -
    volumes:
    -
    -
    environment:
      ZOO_MY_ID:
      ZOO_SERVERS:
    networks:
      kafka:
        ipv4_address:

networks:
  kafka:
    external:
      name:
```

**kafka集群的docker-compose.yml**

```yml
version:

services:
  kafka1:
    image:
    restart:
    hostname:
    container_name:
    privileged:
    ports:
    -
    environment:
      KAFKA_ADVERTISED_HOST_NAME:
      KAFKA_LISTENERS:
      KAFKA_ADVERTISED_LISTENERS:
      KAFKA_ADVERTISED_PORT:
      KAFKA_ZOOKEEPER_CONNECT:
    volumes:
    -
    external_links:
    -
    -
    -
    networks:
      kafka:
        ipv4_address:

  kafka2:
    image:
    restart:
    hostname:
    container_name:
    privileged:
    ports:
    -
    environment:
      KAFKA_ADVERTISED_HOST_NAME:
      KAFKA_LISTENERS:
      KAFKA_ADVERTISED_LISTENERS:
      KAFKA_ADVERTISED_PORT:
      KAFKA_ZOOKEEPER_CONNECT:
    volumes:
    -
    external_links:
    -
    -
    -
    networks:
      kafka:
        ipv4_address:

  kafka3:
    image:
    restart:
    hostname:
    container_name:
    privileged:
    ports:
    -
    environment:
      KAFKA_ADVERTISED_HOST_NAME:
      KAFKA_LISTENERS:
      KAFKA_ADVERTISED_LISTENERS:
      KAFKA_ADVERTISED_PORT:
      KAFKA_ZOOKEEPER_CONNECT:
    volumes:
    -
    external_links:
    -
    -
    -
    networks:
      kafka:
        ipv4_address:

networks:
  kafka:
    external:
      name:
```

**kafka-manager的docker-compose.yml**

```yml
version:

services:
  kafka-manager:
    image:
    restart:
    container_name:
    hostname:
    ports:
     -
    #links:      # 连接本compose文件创建的container
     #- kafka1
     #- kafka2
     #- kafka3
    external_links:
     -
     -
     -
     -
     -
     -
    environment:
     ZK_HOSTS:
     KAFKA_BROKERS:
     APPLICATION_SECRET:
     KM_ARGS:
    networks:
     kafka:
      ipv4_address:

networks:
  kafka:
    external:
      name:
```

**docker-compose up -d 开始部署**

**查看运行中的容器**

```
docker ps 
```

- [\#docker\|kafka\|zookeeper](/tags/docker-kafka-zookeeper/)
