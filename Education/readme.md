# 🔬 Multi-Agent Research Assistant (Agno)

A true multi-agent research system built with **Agno (formerly Phidata)** framework for autonomous research and report generation.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGNO TEAM AGENT                               │
│              (Multi-Agent Coordinator)                           │
└──────────────────┬──────────────────────────────────────────────┘
                   │
        ┏━━━━━━━━━━┻━━━━━━━━━━┓
        ▼                      ▼
┌──────────────┐      ┌────────────────────────────────┐
│PLANNER AGENT │      │      WORKER AGENT              │
│              │      │                                │
│ Role:        │      │ Role: Execution Specialist     │
│ Planning     │─────▶│                                │
│ Expert       │      │ Tools:                         │
│              │      │ ├─ search_web()                │
│ Creates:     │      │ ├─ extract_webpage_content()   │
│ • Research   │      │ ├─ analyze_text_statistics()   │
│   Plan       │      │ ├─ analyze_sentiment()         │
│ • Task List  │      │ └─ create_visualization()      │
│ • Strategy   │      │                                │
└──────────────┘      │ Executes:                      │
                      │ 1. Source Collection           │
                      │ 2. Content Extraction          │
                      │ 3. Data Analysis               │
                      │ 4. Report Writing              │
                      │ 5. Self-Review                 │
                      │ 6. Final Production            │
                      └────────────────────────────────┘
```

## ✨ Key Features

### 🤖 True Multi-Agent System (Agno)
- **Team-based coordination**: Agents work together seamlessly
- **Built-in orchestration**: No manual handoffs needed
- **Tool-equipped agents**: Workers have specialized capabilities
- **Autonomous execution**: Agents make decisions independently

### 📚 Comprehensive Research
- Web search via DuckDuckGo (no API key needed)
- Content extraction from multiple sources
- Text statistics and keyword analysis
- Sentiment analysis
- Auto-generated visualizations

### 📊 Rich Outputs
- Multi-section research reports
- Statistical summaries
- Keyword charts and word clouds
- Sentiment analysis gauges
- Markdown and downloadable formats

## 📁 Project Structure

```
multi-agent-research/
├── app.py                 # Streamlit UI
├── agents.py              # Agno agent definitions
├── orchestrator.py        # Research workflow orchestrator
├── tools.py               # Agent tools (search, extract, analyze)
├── models.py              # Data models
├── config.py              # Configuration
├── logger_setup.py        # Logging
├── requirements.txt       # Dependencies
├── .env.example           # Environment template
└── README.md              # Documentation
```

## 🚀 Installation & Setup

### 1. Prerequisites
- Python 3.9+
- pip

### 2. Clone/Create Project
```bash
mkdir multi-agent-research
cd multi-agent-research
# Copy all files from artifacts
```

### 3. Virtual Environment
```bash
python -m venv venv

# Activate:
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Get Groq API Key (FREE)
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up (no credit card required)
3. Create an API key
4. Free tier includes:
   - 30 requests/minute
   - 6,000 requests/day
   - Plenty for research tasks!

### 6. Configure Environment
```bash
cp .env.example .env
nano .env  # or use any editor

# Add your key:
GROQ_API_KEY=gsk_your_actual_key_here
```

### 7. Run Application
```bash
streamlit run app.py
```

Application opens at: `http://localhost:8501`

## 🎯 Usage

### Basic Workflow

1. **Enter Topic**: Type your research question in the sidebar
   - Example: "Applications of machine learning in healthcare"
   
2. **Click Start**: Agents begin autonomous research
   
3. **Watch Progress**: Real-time status updates show agent activities
   
4. **Review Results**: 
   - Research plan from Planner Agent
   - Complete report from Worker Agent
   - Visualizations and statistics
   
5. **Download**: Get your report in Markdown format

### Example Topics

- "Sentiment analysis applications in social media"
- "Recent advances in quantum computing"
- "Climate change mitigation strategies"
- "Blockchain technology use cases"
- "Artificial intelligence ethics considerations"

## 🛠️ How It Works

### Phase 1: Planning (Planner Agent)
```
Input: Research Topic
↓
Planner Agent analyzes and creates:
├─ Task 1: Source Identification
├─ Task 2: Content Collection
├─ Task 3: Data Analysis
├─ Task 4: Report Drafting
├─ Task 5: Self-Review
└─ Task 6: Final Production
```

### Phase 2: Execution (Worker Agent)
```
Worker Agent with Tools:
│
├─ Task 1: search_web()
│   └─ Find 3-5 trustworthy sources
│
├─ Task 2: extract_webpage_content()
│   └─ Scrape and clean content
│
├─ Task 3: analyze_text_statistics() + analyze_sentiment()
│   └─ Generate statistics and sentiment scores
│
├─ Task 4: LLM-powered writing
│   └─ Draft report sections
│
├─ Task 5: Self-review loop
│   └─ Critique and improve draft
│
└─ Task 6: create_visualization() + formatting
    └─ Final report with charts
```

## ⚙️ Configuration

Edit `config.py`:

```python
# LLM Settings
LLM_MODEL = "llama-3.1-70b-versatile"  # Groq's most capable
LLM_TEMPERATURE = 0.7                   # Creativity level
MAX_TOKENS = 8192                       # Response length

# Research Settings
MAX_SOURCES = 3                         # Sources to collect
MAX_SEARCH_RESULTS = 5                  # Search results to consider

# Review Settings
MAX_REVIEW_ITERATIONS = 2               # Self-review cycles
```

## 🧰 Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Multi-Agent** | Agno (formerly Phidata) | True agent coordination |
| **LLM** | Groq + Llama 3.1 70B | Fast, free, powerful |
| **Search** | DuckDuckGo | No API key needed |
| **Scraping** | BeautifulSoup4 | Reliable extraction |
| **Analysis** | TextBlob | Sentiment analysis |
| **Viz** | Matplotlib, WordCloud | Charts and word clouds |
| **UI** | Streamlit | Clean, reactive interface |
| **Logging** | Loguru | Beautiful logs |

## 📝 Agent Instructions

### Planner Agent
```
Role: Research Planning Expert
Responsibilities:
- Analyze research topic
- Break down into subtasks
- Create structured 6-task plan
- Coordinate with Worker Agent
```

### Worker Agent
```
Role: Research Execution Specialist
Tools: 5 specialized functions
Responsibilities:
- Execute all research tasks
- Use tools autonomously
- Collect and analyze data
- Write and review content
- Produce final outputs
```

## 🐛 Troubleshooting

### "GROQ_API_KEY not found"
```bash
# Check .env file exists
ls -la .env

# Verify contents
cat .env

# Should show:
# GROQ_API_KEY=gsk_...

# Restart app after changes
```

### "Search failed"
- Check internet connection
- DuckDuckGo may rate-limit; wait 30 seconds and retry
- Try a different search query

### "Agent not responding"
- Check Groq API status: [status.groq.com](https://status.groq.com)
- Verify API key is valid
- Check rate limits (30 req/min on free tier)

### Charts not generating
```bash
# Install matplotlib dependencies (Linux)
sudo apt-get install python3-tk

# Verify matplotlib backend
python -c "import matplotlib; print(matplotlib.get_backend())"
# Should show 'Agg'
```

## 🎓 Educational Value

This project demonstrates:
- ✅ Multi-agent coordination (Agno)
- ✅ Tool-equipped agents
- ✅ Autonomous task execution
- ✅ LLM integration (Groq)
- ✅ Web scraping best practices
- ✅ Text analysis techniques
- ✅ Data visualization
- ✅ Clean code architecture
- ✅ Comprehensive logging
- ✅ Modern UI/UX (Streamlit)

## 🔮 Future Enhancements

Possible additions:
- [ ] Add fact-checking agent
- [ ] Implement RAG for better context
- [ ] Add PDF export
- [ ] Include citation management
- [ ] Multi-language support
- [ ] Collaborative editing agent
- [ ] Research history and caching

## 📄 License

MIT License - Free to use and modify!

## 🤝 Contributing

This is an educational project. Feel free to fork and extend!

## 📚 Resources

- [Agno Documentation](https://docs.agno.com)
- [Agno GitHub](https://github.com/agno-agi/agno)
- [Groq Documentation](https://console.groq.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io)

---

**Built with ❤️ using Agno Multi-Agent Framework**