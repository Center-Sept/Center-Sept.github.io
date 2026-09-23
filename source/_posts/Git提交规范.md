---
title: "Git提交规范"
date: 2020-06-24 00:00:00
tags:
  - "git"
categories:
  - "工具"  # 分类为 2026-09 回抄后新加，原文无
description: "一、背景 ​Git每次提交代码都需要写commit message，否则就不允许提交。一般来说，commit message应该清晰明了，说明本次提交的目的，具体做了什么操作……但是在日常开发中，大家的commit message千奇百怪，…"
---
**一、背景**

​Git每次提交代码都需要写commit message，否则就不允许提交。一般来说，commit message应该清晰明了，说明本次提交的目的，具体做了什么操作……但是在日常开发中，大家的commit message千奇百怪，中英文混合使用、fix bug等各种笼统的message司空见怪，这就导致后续代码维护成本特别大，有时自己都不知道自己的fix bug修改的是什么问题。基于以上这些问题，我们希望通过某种方式来监控用户的git commit message，让规范更好的服务于质量，提高大家的研发效率。

**二、规范介绍**

**▐ \**规范目标\****

\- 允许通过脚本生成 README.md

\- 可以通过范围的关键词，快速的搜索到指定版本

```shell
git log HEAD --grep feat(package.json) # 在package.json文件里新增的特性。
```

**▐** *\**\**\*格式要求\*\*\*\**\*

```tex
<type>(<scope>): <subject>
```

\- 消息只占用一行，任何行都不能超过 100 个字符

\- 允许使用 GitHub 以及各种 Git 工具阅读消息

\- 提交消息由页眉、正文和页脚组成，由空行分隔

代表某次提交的类型，比如是修复一个 bug 或是增加一个 feature，类型如下：

| 类型     | 描述                                                      |
|----------|-----------------------------------------------------------|
| feat     | 新增feature                                               |
| fix      | 修复bug                                                   |
| docs     | 仅仅修改了文档，比如README等等                            |
| style    | 修改了空格、格式缩进、逗号等，不改变代码逻辑              |
| refactor | 代码重构，没有加入新的功能或者修复bug                     |
| perf     | 优化相关，比如提升性能、体验                              |
| test     | 测试用例，包括单元测试、集成测试                          |
| chore    | 改变构建流程、或者增加依赖库、工具等，比如修改pom.xml文件 |
| revert   | 回滚上一个版本                                            |
| merge    | 代码合并                                                  |
| sync     | 同步主线活分支的bug                                       |

范围可以是指定提交更改位置的任何内容，如：

\- 对 package.json 文件新增依赖库，chore(package.json): 新增依赖库

\- 或对代码进行重构，refacto(weChat.vue): 重构微信进件

如果没有更合适的范围，可以直接写提交内容
