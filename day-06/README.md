# Day 6: ADK 在各种 IDE 中的集成

> 构建 Agent 不应该花一小时配置环境。Agent Starter Pack 已经内置了 ADK 的 IDE 上下文。

## 今日要点

Day 6 讲的是如何为 AI IDE 提供项目上下文，让 AI 助手更好地帮你开发 Agent。

## 什么是 llms.txt?

`llms.txt` 是一种为 LLM 提供项目文档的标准格式，类似于给搜索引擎的 `robots.txt`。

## IDE 配置文件

| IDE | 配置文件 |
|-----|----------|
| Cursor | `.cursorrules` |
| Claude Code | `.claude/instructions.md` |
| Windsurf | `.windsurfrules` |
| 通用 | `llms.txt` |

## 运行

```bash
# 打开 Jupyter notebook 学习
jupyter notebook day-06/day06_ide_context.ipynb
```

## 资源

- [llms.txt 规范](https://llmstxt.org/)
- [ADK 文档](https://google.github.io/adk-docs/)
- [Antigravity IDE](https://antigravity.google/)
- [视频](https://www.youtube.com/watch?v=Ep8usBDUTtA)
