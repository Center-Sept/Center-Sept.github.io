---
title: "从 200 行代码到生产级 Agent：AI Agent 记忆机制的深度拆解与实战"
date: 2026-08-13 09:00:00
tags:
  - "AI Agent"
  - "大模型"
  - "上下文压缩"
  - "DeepSeek"
  - "开源工具"
categories:
  - "知识精选"
cover: /2026/08/13/agent-memory-from-200-lines/cover.png
slug: agent-memory-from-200-lines
---
## 背景：Agent 时代来了，但记忆是个大问题

2026 年 8 月，AI Agent 领域迎来一波密集发布：

- **DeepSeek V4 Pro 正式版**上线，Agent 能力大幅增强，支持 Responses API 和 Codex 接入
- **Meta 开源 Muse Glimmer**，30B 参数专为本地 Agent 工作流优化
- **Docker 推出 Sandboxes**，为 AI Agent 提供可丢弃的隔离执行环境
- 社区里"手搓 Agent"系列文章热度飙升，开发者开始关注 Agent 的底层机制

但有一个问题始终被忽视：**Agent 的记忆机制**。

当 Agent 只能"活在当下"，每次对话都像第一次见你的时候，它的价值大打折扣。今天，我们就从 200 行代码开始，深度拆解 Agent 的记忆系统，并看看生产级方案是如何解决这个问题的。

---

## 一、为什么 Agent 会"失忆"？

很多初学者写的 Agent 都有这个问题：

```typescript
async run(prompt: string): Promise<string> {
  const messages = [
    { role: "system", content: "..." },
    { role: "user", content: prompt },
  ];
  // 调用模型...
}
```

**问题在哪？** `messages` 是局部变量，函数执行完就消失了。下次再调用 `run()`，Agent 完全不记得之前聊过什么。

这就像你每次见医生都要重新描述一遍病史——效率极低，体验极差。

### 真实场景中的记忆需求

以 **Pi + DeepSeek-v4-Flash** 的实际使用为例（来源：掘金热榜）：

> "排查 Codex Plus 的用量问题，DeepSeek-v4-Flash 会自动识别路径依赖，自动判断这条路是否正确，不会走得太深，判断错了自动更正。"

这种"路径自纠错"能力，依赖于 Agent 对**历史推理路径**的记忆。如果每次都要重新推理，不仅费 token，还容易重复犯错。

---

## 二、基础方案：Session 会话记忆

最简单的解决方案是引入 **Session** 机制：

```typescript
export class Session {
  private readonly history: Message[] = [];
  
  append(...messages: Message[]): void {
    this.history.push(...messages);
  }
  
  getHistory(): Message[] {
    return structuredClone(this.history);
  }
}
```

核心思路：**把消息从局部变量提升到会话级别**。

Agent 每次请求模型时，从 Session 取出完整历史，模型回复后再写回 Session。这样同一个进程内的连续对话就能保持上下文连贯。

### 交互循环：让 Agent"活"在终端里

有了 Session，还需要一个外层循环让程序不退出：

```typescript
while (true) {
  const value = await readline.question("> ");
  if (value === "exit") break;
  await agent.run(value); // 复用同一个 Session
}
```

关键：**Session 和 Agent 在循环外创建**，确保每次用户输入都使用同一份记忆。

---

## 三、进阶挑战：上下文太长怎么办？

Session 能记住历史，但会带来新问题：

**上下文窗口爆炸**。

想象一个场景：Agent 连续读取文件、执行命令、处理报错，消息历史变成这样：

```
用户问题
→ README.md 内容（500 tokens）
→ package.json 内容（300 tokens）
→ 构建日志（2000 tokens）
→ 修改后的文件（800 tokens）
→ 失败堆栈（1500 tokens）
→ 用户新要求
```

如果全部原样发给模型，会出现两个问题：

1. **成本飙升**：输入越长，token 费用越高
2. **关键信息被淹没**：大日志可能把真正重要的新问题挤出上下文

### 解决方案：上下文压缩

核心思想——**把"保存什么"和"这一轮发什么"分开**：

| 存储层 | 作用 |
|--------|------|
| Session.history | 保存完整历史，方便追溯 |
| 工作记忆 | 较早消息的摘要 + 最近消息的原文，作为当前请求输入 |

#### 压缩策略设计

```typescript
interface CompactionState {
  summary: string;      // 压缩后的摘要
  compactedUntil: number; // 压缩到的位置
}

interface UsageSnapshot {
  totalTokens: number;
  historyLength: number;
}
```

**工作流程**：

1. **判断**：用 `usage` 估算当前上下文长度，是否超出预算
2. **切割**：找到安全的分界线（从 user 消息开始保留近期内容）
3. **摘要**：让模型把较早的历史压缩成结构化摘要
4. **合并**：摘要 + 近期原文 = 新的工作记忆

#### 摘要的结构化模板

```markdown
## 用户目标
## 约束与关键决定
## 已完成
## 当前问题
## 已读取或修改的文件
## 下一步
```

这种结构化摘要比纯文本更高效，模型能快速定位关键信息。

---

## 四、生产级实践：Pi + DeepSeek 的启示

**Pi**（minimal terminal coding harness）的设计理念与我们的手搓方案不谋而合：

> "Pi 的重点在于 harness：它负责运行模型、提供工具、保存会话，并允许你替换或扩展几乎所有工作环节。"

Pi 的核心优势：

| 特性 | 说明 |
|------|------|
| 模型自由 | 支持多 Provider，一键切换 |
| 工作流自定义 | 不强制 Plan/Subagent，按需组合 |
| Skill 复用 | 支持 .agents/skills、Claude Code、Codex 的 Skill |
| 嵌入能力 | 提供 JSON、RPC、TypeScript SDK |

**接入 DeepSeek-v4-Flash 的配置示例**：

```json
{
  "providers": {
    "deepseek": {
      "baseUrl": "https://api.deepseek.com/v1",
      "apiKey": "***",
      "models": [{
        "id": "deepseek-v4-flash",
        "contextWindow": 1000000,
        "maxTokens": 65536
      }]
    }
  }
}
```

**实际效果**：

> "20M token 不到 1 块钱，同样的排查量级，GPT 那边是直接烧掉半个 plus 号的周额度。"

> "1M 上下文：支持长项目和长报告。路径自纠错：干活的适合发现走错路会自动退回来换一条。"

这说明**长上下文 + 记忆机制**的组合，是 Agent 高效工作的关键。

---

## 五、更远的未来：本地 Agent 与边缘推理

Meta 最新开源的 **Muse Glimmer** 代表了另一个方向：

- **30B 参数**，专为本地 Agent 工作流优化
- 单张消费级 GPU 或 Mac/PC 即可完成部署
- 量化后体积压缩至 20GB 以内
- 推测解码机制将推理速度提升 3.1 倍

配合 **Docker Sandboxes** 的隔离执行环境，本地 Agent 的安全性和可用性大幅提升。

**DeepSeek-V4-Flash 的浏览器端部署**也值得关注：

> "在浏览器里本地运行 DeepSeek-R1 1.5B，全程不需要后端服务器，所有 AI 计算都在用户设备上完成。"

使用 **Transformer.js + WebGPU**，前端也能跑大模型：

```javascript
import { AutoTokenizer, AutoModelForCausalLM } 
  from "@huggingface/transformers";

const tokenizer = await AutoTokenizer.from_pretrained("model-id");
const model = await AutoModelForCausalLM.from_pretrained("model-id");
```

首次下载约 800MB（缓存后秒开），推理速度比 CPU 快 5-20 倍。

---

## 六、实践启示：如何设计你的 Agent 记忆系统

### 1. 分层存储架构

```
┌─────────────────────────────────────┐
│  工作记忆（短期）                      │
│  - 最近 3-5 轮对话原文                │
│  - 当前任务上下文                      │
├─────────────────────────────────────┤
│  会话摘要（中期）                      │
│  - 结构化摘要                        │
│  - 关键决策和文件记录                  │
├─────────────────────────────────────┤
│  持久存储（长期）                      │
│  - PLAN.md / TODO.md                 │
│  - 向量数据库（RAG）                  │
└─────────────────────────────────────┘
```

### 2. 关键设计原则

| 原则 | 说明 |
|------|------|
| 延迟加载 | 不要一次性加载全部历史，按需获取 |
| 分层压缩 | 近期原文 + 中期摘要 + 长期向量 |
| 结构化摘要 | 使用固定模板，提高信息密度 |
| 安全回退 | 压缩失败时截断而非报错 |

### 3. 成本与效果的平衡

以 **DeepSeek-v4-Flash** 为例：

- 1M 上下文窗口，足以容纳大部分项目的完整代码库
- 20M token 不到 1 元，成本极低
- 但超过上下文上限后，压缩机制必须介入

**建议阈值**：

```
可用 Token = contextWindow - reserveTokens(16k) 
           - 当前请求预估(4k)

当历史占用 > 可用 Token 的 80% 时触发压缩
```

---

## 结语：Agent 的"记忆"是智能的基石

从 200 行代码的手搓 Session，到生产级的上下文压缩，再到本地部署的边缘推理——Agent 的记忆机制正在快速进化。

**关键认知**：

1. **记忆不是存储，是注意力管理**——决定什么该保留、什么该压缩
2. **结构化优于纯文本**——模板化摘要提高信息密度
3. **长上下文是趋势，但压缩仍必要**——1M token 也会用完
4. **本地部署降低延迟和成本**——Muse Glimmer、DeepSeek-V4-Flash 代表方向

当 Agent 能记住你上周的需求、上个月的设计决策、去年的项目架构时，它才真正从"工具"变成"伙伴"。

---

**参考资源**：

- [不用LangChain：用 200 行代码手搓 Agent 对话记忆与上下文压缩](https://juejin.cn/post/7671855098491043866)
- [Pi + DeepSeek-v4-Flash，这用着也太爽了](https://juejin.cn/post/7671964740780785670)
- [从零在浏览器里跑 DeepSeek-R1：WebGPU + Transformer.js 全链路实战](https://juejin.cn/post/7671475529255321610)
- [IT早报：DeepSeek V4 Pro 正式版更新](https://www.ithome.com/0/989/023.htm)
- [派早报：Meta 发布开源本地 AI 智能体大模型 Muse Glimmer](https://sspai.com/post/113301)
