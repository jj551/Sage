# Sage - AI-Powered Data Analysis Framework

Sage is a powerful AI-driven data analysis assistant framework that combines Large Language Models (LLMs) to provide natural language interaction for data exploration, analysis, and visualization.

## 📋 Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation Guide](#installation-guide)
- [Quick Start](#quick-start)
- [Usage Instructions](#usage-instructions)
- [Module Documentation](#module-documentation)
- [Roadmap](#roadmap)

## ✨ Features

### 🤖 Intelligent Interaction
- Natural language-driven data analysis
- Context-aware session management
- Automatic task planning and execution

### 📊 Data Processing
- Support for multiple data sources (CSV, Excel, Parquet)
- Data cleaning and preprocessing
- Descriptive statistics and correlation analysis
- Feature engineering
- Outlier detection

### 🎨 Visualization
- Automatic chart type selection
- Support for line charts, bar charts, scatter plots, heatmaps, and more
- Base64 encoded image output
- Automatic chart saving

### 🔧 Enterprise-Grade Features
- LLM response caching
- Rate limiting
- Cost tracking and budget alerts
- Session persistence

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Layer                                │
│  ┌─────────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ CommandParser   │  │ OutputRenderer│  │    REPL      │  │
│  └─────────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Session Management Layer                   │
│                    SessionManager                            │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Agent Core Layer                           │
│  ┌──────────────────┐         ┌──────────────────────┐      │
│  │  TaskPlanner     │◄───────►│  ToolCoordinator    │      │
│  └──────────────────┘         └──────────────────────┘      │
│                    SageAgent                                   │
└─────────────────────────────────────────────────────────────┘
         │                           │
         ▼                           ▼
┌──────────────────┐       ┌─────────────────────────┐
│  LLM Gateway     │       │     Tool Execution      │
│ ┌──────────────┐ │       │ ┌─────────────────────┐ │
│ │LLMAPIGateway │ │       │ │ DataAccessModule    │ │
│ ├──────────────┤ │       │ ├─────────────────────┤ │
│ │Adapters      │ │       │ │AnalysisExecutionMod │ │
│ │ResponseCache │ │       │ ├─────────────────────┤ │
│ │RateLimiter   │ │       │ │ResultProcessingMod  │ │
│ │CostTracker   │ │       │ └─────────────────────┘ │
│ └──────────────┘ │       └─────────────────────────┘
└──────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Data Storage Layer                          │
│  ┌──────────────────┐  ┌──────────────┐                     │
│  │ExternalDataSource│  │  MetadataDB  │                     │
│  └──────────────────┘  └──────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Installation Guide

### Requirements
- Python 3.8+
- pip

### Install Dependencies

```bash
cd sage
pip install -r requirements.txt
```

Or install manually:

```bash
pip install pandas numpy matplotlib seaborn tabulate diskcache click prompt_toolkit pygments plotext
```

## 🚀 Quick Start

### Configure LLM API (Optional)

Sage supports multiple LLM providers and uses mock mode by default.

1. Copy the environment variable example file:
```bash
cp .env.example .env
```

2. Edit the `.env` file and add your API Key:
```env
# OpenAI
OPENAI_API_KEY=sk-your-key-here
SAGE_MODEL=gpt-3.5-turbo

# Or Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
SAGE_MODEL=claude-3-haiku-20240307

# Or DeepSeek
DEEPSEEK_API_KEY=sk-your-deepseek-key
SAGE_MODEL=deepseek-chat

# Or local Ollama
OLLAMA_BASE_URL=http://localhost:11434
SAGE_MODEL=llama3
```

### 1. Using Python API

```python
from src.agent_core.agent import SageAgent

# Initialize Agent (uses mock-model by default)
agent = SageAgent()

# Or specify a model
# agent = SageAgent(config={'model': 'gpt-3.5-turbo'})

# Create a session
session_id = agent.create_session()
print(f"Session ID: {session_id}")

# Natural language interaction
response = agent.process_message("load the sales data")
print(response)

response = agent.process_message("show descriptive statistics")
print(response)
```

### 2. Using Command Line

```bash
# Enter interactive mode
python3 main.py chat

# Single query
python3 main.py query "analyze the sales data"

# Check version
python3 main.py --version
```

## 📖 Usage Instructions

### Supported Data Sources

Sage supports the following data sources:

- **Local Files**: CSV, Excel, Parquet
  - Example: `file://path/to/data.csv`
- **Database** (coming soon): `db://connection/table`
- **S3** (coming soon): `s3://bucket/path`

### Available Tools

| Tool Name | Description |
|-----------|-------------|
| `load_data` | Load dataset |
| `descriptive_stats` | Descriptive statistical analysis |
| `plot_trend` | Plot trend chart |
| `correlation` | Correlation analysis and heatmap |
| `clean_data` | Data cleaning |
| `feature_engineering` | Feature engineering |
| `outlier_detection` | Outlier detection |
| `respond` | Natural language response |

### Data Analysis Features

```python
# Data cleaning
agent._tool_clean_data(drop_na=True, fill_na='mean')

# Feature engineering
agent._tool_feature_engineering(
    date_columns=['date'],
    categorical_columns=['category'],
    one_hot_encode=True
)

# Outlier detection
agent._tool_outlier_detection(column='sales', method='iqr')

# Correlation analysis
agent._tool_correlation()
```

## 📦 Module Documentation

### agent_core/
- **agent.py**: Main `SageAgent` class, integrates all modules
- **task_planner.py**: Task planner, generates execution plans
- **tool_coordinator.py**: Tool coordinator, executes plan steps

### llm_gateway/
- **llm_api_gateway.py**: Unified LLM API gateway
- **adapters.py**: Multi-provider adapters (OpenAI, Anthropic, DeepSeek, Ollama)
- **cost_tracker.py**: Cost tracking and budget management
- **rate_limiter.py**: Rate limiting (token bucket algorithm)
- **response_cache.py**: LLM response caching

### tool_execution/
- **data_access.py**: Data access module
- **analysis_execution.py**: Analysis execution module (cleaning, stats, feature engineering)
- **result_processing.py**: Result processing (visualization, summarization)

### data_storage/
- **external_data_source.py**: External data source connection management
- **metadata_db.py**: Metadata database (tasks, dataset records)

### session_management/
- **session_manager.py**: Session persistence management (SQLite)

### cli/
- **command_parser.py**: Click command parser
- **output_renderer.py**: Output rendering (text, tables, charts)
- **repl.py**: Interactive REPL

## 🔮 Roadmap

- [x] Integrate real LLM APIs (OpenAI, Anthropic, Ollama, DeepSeek)
- [ ] Database connection support (SQLAlchemy)
- [ ] S3 cloud storage support
- [ ] Machine learning model training (scikit-learn, XGBoost)
- [ ] Hyperparameter tuning (Optuna)
- [ ] HTML/PDF report generation
- [ ] Parallel task execution
- [ ] Containerized execution isolation
- [ ] Web UI interface

## 🤖 LLM Integration

### Supported Models

Sage supports multiple LLM providers:

| Provider | Example Models | Environment Variables |
|----------|----------------|----------------------|
| **OpenAI** | `gpt-3.5-turbo`, `gpt-4`, `gpt-4o` | `OPENAI_API_KEY` |
| **Anthropic** | `claude-3-haiku-20240307`, `claude-3-sonnet-20240229` | `ANTHROPIC_API_KEY` |
| **DeepSeek** | `deepseek-chat`, `deepseek-coder` | `DEEPSEEK_API_KEY` |
| **Ollama** | `llama2`, `llama3`, `mistral`, `gemma` | `OLLAMA_BASE_URL`, `OLLAMA_API_KEY` |
| **Mock** | `mock-model` (default) | - |

### Configuration Steps

1. **Copy configuration file**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env file**
   
   **Using OpenAI:**
   ```env
   OPENAI_API_KEY=sk-your-actual-api-key
   SAGE_MODEL=gpt-3.5-turbo
   ```
   
   **Using Anthropic:**
   ```env
   ANTHROPIC_API_KEY=sk-ant-your-actual-api-key
   SAGE_MODEL=claude-3-haiku-20240307
   ```
   
   **Using DeepSeek:**
   ```env
   DEEPSEEK_API_KEY=sk-your-deepseek-key
   SAGE_MODEL=deepseek-chat
   ```
   
   **Using local Ollama:**
   ```env
   OLLAMA_BASE_URL=http://localhost:11434
   SAGE_MODEL=llama3
   ```

3. **Test configuration**
   ```bash
   python3 test_llm_integration.py
   ```

### Fallback Mechanism

If API Key is not configured or the call fails, the framework automatically falls back to mock mode to ensure functionality remains available.

## 📄 License

This project is for learning and research purposes only.

## 🤝 Contributing

Issues and Pull Requests are welcome!

---

**Sage** - Making data analysis simple and powerful! 💡
