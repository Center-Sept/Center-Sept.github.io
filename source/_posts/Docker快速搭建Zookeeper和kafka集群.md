---
title: "Docker快速搭建Zookeeper和kafka集群"
date: 2021-07-24 00:00:00
tags:
  - "docker|kafka|zookeeper"
categories:
  - "运维"  # 分类为 2026-09 回抄后新加，原文无
description: "前提：安装docker和docker-compose 镜像选择 实现目标 拉取镜像 创建集群网络 查看网络 zk集群的docker-compose.yml（任意目录下创建docker-compose.yml文件） kafka集群的docke…"
---
# 安装

**前提：安装docker和docker-compose**

**镜像选择**

```plaintext
Zookeeper和Kafka集群分别运行在不同的容器中
zookeeper官方镜像，版本3.4 （zookeeper:3.4）
kafka采用wurstmeister/kafka镜像
kafka-manager采用sheepkiller/kafka-manager:latest镜像
```

**实现目标**

```plaintext
kafka集群在docker网络中可用，和zookeeper处于同一网络
宿主机可以访问zookeeper集群和kafka的broker list
docker重启时集群自动重启
集群的数据文件映射到宿主机器目录中
使用yml文件和$ docker-compose up -d命令创建或重建集群
```

**拉取镜像**

```plaintext
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
version: '3.4'

services:
  zoo1:
    image: zookeeper:3.4
    restart: always
    hostname: zoo1
    container_name: zoo1
    ports:
    - 2184:2181
    volumes:
    - "./cluster/zoo1/data:/data"
    - "./cluster/zoo1/datalog:/datalog"
    environment:
      ZOO_MY_ID: 1
      ZOO_SERVERS: server.1=0.0.0.0:2888:3888 server.2=zoo2:2888:3888 server.3=zoo3:2888:3888
    networks:
      kafka:
        ipv4_address: 172.19.0.11


  zoo2:
    image: zookeeper:3.4
    restart: always
    hostname: zoo2
    container_name: zoo2
    ports:
    - 2185:2181
    volumes:
    - "./cluster/zoo2/data:/data"
    - "./cluster/zoo2/datalog:/datalog"
    environment:
      ZOO_MY_ID: 2
      ZOO_SERVERS: server.1=zoo1:2888:3888 server.2=0.0.0.0:2888:3888 server.3=zoo3:2888:3888
    networks:
      kafka:
        ipv4_address: 172.19.0.12


  zoo3:
    image: zookeeper:3.4
    restart: always
    hostname: zoo3
    container_name: zoo3
    ports:
    - 2186:2181
    volumes:
    - "./cluster/zoo3/data:/data"
    - "./cluster/zoo3/datalog:/datalog"
    environment:
      ZOO_MY_ID: 3
      ZOO_SERVERS: server.1=zoo1:2888:3888 server.2=zoo2:2888:3888 server.3=0.0.0.0:2888:3888
    networks:
      kafka:
        ipv4_address: 172.19.0.13


networks:
  kafka:
    external:
      name: kafka
```

**kafka集群的docker-compose.yml**

```yml
version: '2'

services:
  kafka1:
    image: wurstmeister/kafka
    restart: always
    hostname: kafka1
    container_name: kafka1
    privileged: true
    ports:
    - 9092:9092
    environment:
      KAFKA_ADVERTISED_HOST_NAME: kafka1
      KAFKA_LISTENERS: PLAINTEXT://kafka1:9092
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka1:9092
      KAFKA_ADVERTISED_PORT: 9092
      KAFKA_ZOOKEEPER_CONNECT: zoo1:2181,zoo2:2181,zoo3:2181
    volumes:
    - ./cluster/kafka1/data:/kafka
    external_links:
    - zoo1
    - zoo2
    - zoo3
    networks:
      kafka:
        ipv4_address: 172.19.0.21


  kafka2:
    image: wurstmeister/kafka
    restart: always
    hostname: kafka2
    container_name: kafka2
    privileged: true
    ports:
    - 9093:9093
    environment:
      KAFKA_ADVERTISED_HOST_NAME: kafka2
      KAFKA_LISTENERS: PLAINTEXT://kafka2:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka2:9093
      KAFKA_ADVERTISED_PORT: 9093
      KAFKA_ZOOKEEPER_CONNECT: zoo1:2181,zoo2:2181,zoo3:2181
    volumes:
    - ./cluster/kafka2/data:/kafka
    external_links:
    - zoo1
    - zoo2
    - zoo3
    networks:
      kafka:
        ipv4_address: 172.19.0.22


  kafka3:
    image: wurstmeister/kafka
    restart: always
    hostname: kafka3
    container_name: kafka3
    privileged: true
    ports:
    - 9094:9094
    environment:
      KAFKA_ADVERTISED_HOST_NAME: kafka3
      KAFKA_LISTENERS: PLAINTEXT://kafka3:9094
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka3:9094
      KAFKA_ADVERTISED_PORT: 9094
      KAFKA_ZOOKEEPER_CONNECT: zoo1:2181,zoo2:2181,zoo3:2181
    volumes:
    - ./cluster/kafka3/data:/kafka
    external_links:
    - zoo1
    - zoo2
    - zoo3
    networks:
      kafka:
        ipv4_address: 172.19.0.23


networks:
  kafka:
    external:
      name: kafka
```

**kafka-manager的docker-compose.yml**

```yml
version: "2"

services:
  kafka-manager:
    image: sheepkiller/kafka-manager:latest
    restart: always
    container_name: kafka-manager
    hostname: kafka-manager
    ports:
     - "9000:9000"
    #links:      # 连接本compose文件创建的container
     #- kafka1
     #- kafka2
     #- kafka3
    external_links:  # 连接本compose文件以外的container
     - kafka1
     - kafka2
     - kafka3
     - zoo1
     - zoo2
     - zoo3
    environment:
     ZK_HOSTS: zoo1:2181,zoo2:2181,zoo3:2181
     KAFKA_BROKERS: kafka1:9092,kafka2:9093,kafka3:9094
     APPLICATION_SECRET: letmein
     KM_ARGS: -Djava.net.preferIPv4Stack=true
    networks:
     kafka:
      ipv4_address: 172.19.0.9

networks:
  kafka:
    external:
      name: kafka
```

**docker-compose up -d 开始部署**

**查看运行中的容器**

```plaintext
docker ps 
```
