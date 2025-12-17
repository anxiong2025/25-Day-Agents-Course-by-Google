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
| 01 | Introduction to AI Agents | 🚧 In Progress |
| 02 | TBD | ⏳ Pending |
| ... | ... | ... |

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
