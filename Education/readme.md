# 🔬 Multi-Agent Research Assistant

A simple, educational implementation of a multi-agent system that autonomously conducts research and generates reports.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                              │
│  Coordinates the workflow between agents                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
┌───────────────┐           ┌───────────────────────────────┐
│ PLANNER AGENT │           │        WORKER AGENT           │
│               │           │                               │
│ • Analyzes    │           │  ┌─────────────────────────┐  │
│   topic       │──────────▶│  │ A) Data Collector       │  │
│ • Creates     │           │  │    - DuckDuckGo Search  │  │
│   plan        │           │  │    - Web Scraping       │  │
│ • Defines     │           │  └─────────────────────────┘  │
│   tasks       │           │  ┌─────────────────────────┐  │
└───────────────┘           │  │ B) Analyzer             │  │
                            │  │    - Text Statistics    │  │
                            │  │    - Sentiment Analysis │  │
                            │  │    - Visualization      │  │
                            │  └─────────────────────────┘  │
                            │  ┌─────────────────────────┐  │
                            │  │ C) Report Writer        │  │
                            │  │    - Section Generation │  │
                            │  │    - Markdown/HTML      │  │
                            │  └─────────────────────────┘  │
                            │  ┌─────────────────────────┐  │
                            │  │ D) Self-Reviewer        │  │
                            │  │    - Critiques Draft    │  │
                            │  │    - Improves Content   │  │
                            │  └─────────────────────────┘  │
                            └───────────────────────────────┘
```

## 📁 Project Structure

```
multi-agent-research/
├── app.py                 # Streamlit UI
├── orchestrator.py        # Coordinates agents
├── planner_agent.py       # Planning agent
├── worker_agent.py        # Execution agent
├── data_collector.py      # Web search & scraping
├── analyzer.py            # Text analysis
├── report_generator.py    # Report creation
├── llm_client.py          # Groq API wrapper
├── models.py              # Data models
├── config.py              # Configuration
├── logger_setup.py        # Logging setup
├── requirements.txt       # Dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Clone/Create Project

```bash
mkdir multi-agent-research
cd multi-agent-research
# Copy all the files from the artifacts
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Free API Key

1. Go to [Groq Console](https://console.groq.com)
2. Sign up for free
3. Create an API key

### 5. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 6. Run the Application

```bash
streamlit run app.py
```

## 🎯 How It Works

### Step 1: User Input
Enter a research topic like "Sentiment analysis applications in social media"

### Step 2: Planner Agent
- Breaks down the research into 6 tasks
- Creates a structured plan
- Assigns tasks to Worker Agent

### Step 3: Worker Agent Executes
| Phase | Action |
|-------|--------|
| **A) Collection** | Searches DuckDuckGo, extracts content from top 3 sources |
| **B) Analysis** | Runs text statistics, keyword extraction, sentiment analysis |
| **C) Writing** | Generates report sections using LLM |
| **D) Review** | Self-critiques and improves the draft |

### Step 4: Final Output
- Clean research report (Markdown + HTML)
- Statistical analysis
- Visualizations (keyword chart, word cloud, sentiment gauge)

## 📊 Features

### ✅ Multi-Agent Architecture
- **Planner Agent**: Strategic planning with LLM
- **Worker Agent**: Autonomous task execution

### ✅ Data Collection
- DuckDuckGo search (no API key needed)
- BeautifulSoup web scraping
- Smart content extraction

### ✅ Analysis Capabilities
- Word count & sentence statistics
- Keyword frequency analysis
- Sentiment analysis with TextBlob
- Auto-generated visualizations

### ✅ Report Generation
- Multiple sections (Summary, Introduction, Findings, Analysis, Conclusion)
- Markdown and HTML output
- Source citations

### ✅ Self-Review Loop
- Automatic draft improvement
- Iterative refinement
- Quality assurance

### ✅ Clean UI/UX
- Modern Streamlit interface
- Real-time task progress
- Detailed agent logs
- Download options

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# LLM Settings
LLM_MODEL = "llama-3.1-8b-instant"  # Fast and free
LLM_TEMPERATURE = 0.7
MAX_TOKENS = 4096

# Research Settings
MAX_SOURCES = 3          # Number of sources to collect
MAX_SEARCH_RESULTS = 5   # Search results to consider

# Review Settings
MAX_REVIEW_ITERATIONS = 2  # Self-review cycles
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **LLM** | Groq (Llama 3.1 8B) |
| **Search** | DuckDuckGo (free) |
| **Scraping** | BeautifulSoup |
| **Analysis** | TextBlob, NLTK |
| **Visualization** | Matplotlib, WordCloud |
| **UI** | Streamlit |
| **Logging** | Loguru |

## 💡 Tips

1. **Better Results**: Use specific, focused research topics
2. **Source Quality**: The system prioritizes authoritative sources
3. **Logs**: Enable detailed logs to understand agent behavior
4. **Iteration**: Increase `MAX_REVIEW_ITERATIONS` for better quality

## 🐛 Troubleshooting

### "GROQ_API_KEY not found"
- Ensure `.env` file exists with your API key
- Restart the application after editing `.env`

### "Search failed"
- Check internet connection
- DuckDuckGo may rate-limit; wait and retry

### "Content extraction failed"
- Some sites block scraping
- The system falls back to search snippets

## 📝 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

This is an educational project. Feel free to:
- Add more agents (Fact-checker, Editor, etc.)
- Implement RAG for better context
- Add more output formats
- Improve the UI
