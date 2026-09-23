---
title: "kubernetes集群搭建"
date: 2022-05-05 00:00:00
tags:
  - "kubernetes"
categories:
  - "运维"  # 分类为 2026-09 回抄后新加，原文无
description: "1.一台16G及以上的电脑 2.window系统 3.安卓 VMware pro 17 4.分别创建三个centos7 mini 的虚拟主机，硬件配置按需配置最好是2核2G或以上，网络模式使用桥连 5.分别配置好静态ip地址和hostnam…"
---
## 环境准备

1.一台16G及以上的电脑

2.window系统

3.安卓 VMware pro 17

4.分别创建三个centos7 mini 的虚拟主机，硬件配置按需配置最好是2核2G或以上，网络模式使用桥连

5.分别配置好静态ip地址和hostname

## Docker容器化安装

```shell
# 首先安装工具类
yum install -y yum-utils
# 配置docker的yum源
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
# 安装docker
sudo yum install -y docker-ce docker-ce-cli containerd.io
# 可以指定版本来安装，这里是安装最新版本，所以要寻找最新版本的k8s来支持
yum install -y docker-ce-20.10.7 docker-ce-cli-20.10.7 containerd.io-1.4.6
# 启动docker
systemctl enable docker --now

# 添加了docker的生产环境核心配置cgroup
sudo mkdir -p /etc/docker 
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://reg-mirror.qiniu.com/","https://5wdlar25.mirror.aliyuncs.com","https://hub-mirror.c.163.com/","https://docker.mirrors.ustc.edu.cn/"],
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2"
}
EOF
# 加载配置 重启docker
sudo systemctl daemon-reload && sudo systemctl restart docker

```

## 预备环境搭建

```bash
# 修改hostname，用于主机间的通讯
hostnamectl set-hostname k8s-master
hostnamectl set-hostname k8s-node1
hostnamectl set-hostname k8s-node2
# 刷新修改之后的操作
bash
#将SELinux设置为permissive模式（相当于将其禁用）
sudo setenforce 0
sudo sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config
# 关闭交换空间
swapoff -a
sed -ri 's/.*swap.*/#&/' /etc/fstab
# 转发 IPv4 并让 iptables 看到桥接流量
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter

# 设置所需的 sysctl 参数，参数在重新启动后保持不变
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

# 应用 sysctl 参数而不重新启动
sudo sysctl --system

# 通过运行以下指令确认 br_netfilter 和 overlay 模块被加载
lsmod | grep br_netfilter
lsmod | grep overlay

# 通过运行以下指令确认 net.bridge.bridge-nf-call-iptables、net.bridge.bridge-nf-call-ip6tables 和 net.ipv4.ip_forward 系统变量在你的 sysctl 配置中被设置为 1
sysctl net.bridge.bridge-nf-call-iptables net.bridge.bridge-nf-call-ip6tables net.ipv4.ip_forward

```

## 集群三大组件安装（kubeadm、kubectl、kubelet）

```bash
cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=http://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=0
repo_gpgcheck=0
gpgkey=http://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg
   http://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
exclude=kubelet kubeadm kubectl
EOF


sudo yum install -y kubelet-1.20.9 kubeadm-1.20.9 kubectl-1.20.9 --disableexcludes=kubernetes

sudo systemctl enable --now kubelet
```

## 使用kubeadm引导集群

### 下载各个机器需要的镜像

```bash
sudo tee ./images.sh <<-'EOF'
#!/bin/bash
images=(
kube-apiserver:v1.20.9
kube-proxy:v1.20.9
kube-controller-manager:v1.20.9
kube-scheduler:v1.20.9
coredns:1.7.0
etcd:3.4.13-0
pause:3.2
)
for imageName in ${images[@]} ; do
docker pull registry.cn-hangzhou.aliyuncs.com/lfy_k8s_images/$imageName
done
EOF
   
chmod +x ./images.sh && ./images.sh
```

### 初始化主节点

```bash
#所有机器添加master域名映射，以下需要修改为自己的
echo "{你的主节点内网主机ip}  cluster-endpoint" >> /etc/hosts

# ping一下是否能通讯
ping cluster-endpoint

# 主节点初始化，只在你选定的主节点服务器执行一下命令
# apiserver-advertise-address、 service-cidr 和 pod-network-cidr 所有网络范围不重叠
kubeadm init \
--apiserver-advertise-address=192.168.0.201 \
--control-plane-endpoint=cluster-endpoint \
--image-repository registry.cn-hangzhou.aliyuncs.com/lfy_k8s_images \
--kubernetes-version v1.20.9 \
--service-cidr=10.96.0.0/16 \
--pod-network-cidr=192.188.0.0/16

# 执行完成以上命令后，把Your Kubernetes control-plane has initialized successfully!语句之后的文本复制下来，之后会使用到
# 执行文本中的命令
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# 如果不小心清屏了,用一下命令重置一下 
kubeadm reset

# 再执行成功后的命令，重写$HOME/.kube/config文件

# 查看集群所有节点
kubectl get nodes

# 下面来安装网络插件
curl https://docs.projectcalico.org/v3.20/manifests/calico.yaml -O
# 注意，如果你修改了 初始化命令的pod-network-cidr参数，需要编辑calico.yaml文件，找到192.168.0.0参数，修改为你修改的参数192.188.0.0，释放键值的注释
kubectl apply -f calico.yaml

# 使用初始化之后的信息，将工作节点加入到集群中
kubeadm join cluster-endpoint:6443 --token hijbfi.ewcww5noqyztfgsa \
    --discovery-token-ca-cert-hash sha256:2c2b1c21e175f7eaa0692e8fad349af599adbd0f53118d0f48101aacbd3be142

# 如果以上命令的令牌已经过期，可以使用一下命令来生成令牌
kubeadm token create --print-join-command

# 在主节点服务器使用一下命令查看工作节点的初始化状态
watch -n 1 kubectl get pod -A

# 都是running状态之后，再用 kubectl get nodes查看节点信息是否已经ready状态
```

最后重启所有节点机器，测试一下集群的修复能力。如果启动失败，看看是不是docker服务是不是没有启动。

### 部署可视化

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.3.1/aio/deploy/recommended.yaml
# 如果以上命令下载不了，可以配置hosts定位ip
# 也可以使用浏览器打开以上地址，然后 vi dashboard.yaml创建文件，把文本内容粘贴到里面
# 再用以下命令创建容器
kubectl apply -f dashboard.yaml

```
