# 25-Day AI Agents Course by Google

A hands-on learning journey through Google's AI Agents capabilities.

> **Official Course**: [Advent of Agents 2025](https://adventofagents.com/) - 25 days of Zero to Production-Ready AI Agents on Google Cloud

## About This Course

This is Google Cloud's **Advent of Agents 2025** program - a 25-day journey to master AI Agents using:
- **Gemini 3** - Google's latest AI models
- **Agent Development Kit (ADK)** - Comprehensive agent development platform
- **Agent Engine** - Production deployment infrastructure

### Course Highlights
- 🎯 One feature per day, each taking less than 5 minutes to try
- 📋 Copy-paste commands that work out of the box
- 📚 Links to official documentation
- 🆓 100% free

> 📖 **Prerequisite**: [5-Day AI Agents Intensive Course](https://github.com/anxiong2025/5-Day-AI-Agents-Intensive-Course-with-Google) - Google's foundational course on AI Agents

### Difficulty Curve

<p align="center">
  <img src="assets/difficulty_curve.svg" alt="Course Difficulty Curve" width="600">
</p>

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Install dependencies
uv sync

# Create .env file and add your API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

## Project Structure

```
.
├── day-01/                 # Day 1: Introduction
├── day-02/                 # Day 2: ...
├── ...
├── shared/                 # Shared utilities
│   ├── __init__.py
│   └── config.py          # Configuration helpers
├── pyproject.toml         # Project dependencies
└── README.md
```

## Daily Progress

| Day | Topic | Status |
|-----|-------|--------|
| 01 | Introduction to AI Agents | ✅ Done |
| 02 | YAML Agent Configuration | ✅ Done |
| 03 | Gemini Search Agent | ✅ Done |
| 04 | Agent Engine Deployment | ✅ Done |
| 05 | Telemetry & Tracing | ✅ Done |
| 06 | ADK IDE Integration | ✅ Done |
| 07 | Code Execution | ✅ Done |
| 08 | Context Management | ✅ Done |
| 09 | Session Rewind | ✅ Done |
| 10 | Context Caching & Compaction | ✅ Done |
| 11 | Google Managed MCP | ✅ Done |
| 12 | Multimodal Streaming Agents | ✅ Done |
| 13 | Interactions API | ✅ Done |
| 14 | A2A Remote Agents | ✅ Done |
| 15 | Agent-to-UI | ✅ Done |
| 16 | LangGraph + A2A | ✅ Done |
| 17 | Gemini 3 Flash Thinking Levels | ✅ Done |
| 18 | Cloud API Registry + ADK | ✅ Done |
| 19 | Register to Gemini Enterprise | ✅ Done |
| 20 | A2A Extensions: Secure Passport | ✅ Done |
| 21 | Kaggle Capstone 获奖项目分析 | ✅ Done |
| 22-25 | Enterprise Topics | ⏳ Pending |

## Running Daily Exercises

```bash
# Run day 1 exercises
uv run python day-01/main.py

# Run with dev dependencies (for testing)
uv sync --dev
uv run pytest
```

## Resources

- [Advent of Agents 2025](https://adventofagents.com/) - Official course website
- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
