---
title: 博客回来了：hexo + butterfly，源进仓、Actions 发布
date: 2026-09-20 09:00:00
tags:
  - 博客
  - hexo
categories:
  - 站务
slug: hello-hexo-butterfly
---

旧站（2020–2023 的 15 篇）是 `hexo deploy` 直推的产物，源丢了。这次把源放进仓的 `source` 分支，由 GitHub Actions 构建后发到 Pages；旧文从产物 HTML 回抄成 markdown，15 个旧地址一个不变。

- 生成器：hexo 8.1.2，主题 butterfly 5.7.0
- permalink：`:year/:month/:day/:title/`，与旧站相同
- 新文文件名一律 ASCII slug，本篇是第一篇：`/2026/09/20/hello-hexo-butterfly/`

从这一篇起，文章由内容系统（fuxi 发布段）出包，人只在推送前按一次「发」。
