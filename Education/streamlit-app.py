"""
Streamlit UI for the Multi-Agent Research Assistant.
Clean, modern interface with step-by-step visibility.
"""
import streamlit as st
from datetime import datetime
from pathlib import Path
import time

# Page config
st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main theme */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #e94560 !important;
    }
    
    /* Cards */
    .agent-card {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #e94560;
    }
    
    .task-card {
        background: rgba(255,255,255,0.03);
        border-radius: 8px;
        padding: 15px;
        margin: 8px 0;
        transition: all 0.3s ease;
    }
    
    .task-pending { border-left: 3px solid #6c757d; }
    .task-progress { border-left: 3px solid #ffc107; background: rgba(255,193,7,0.1); }
    .task-complete { border-left: 3px solid #28a745; }
    .task-failed { border-left: 3px solid #dc3545; }
    
    /* Log entries */
    .log-entry {
        font-family: 'Monaco', monospace;
        font-size: 0.85em;
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 6px;
        background: rgba(0,0,0,0.2);
    }
    
    .log-planner { border-left: 3px solid #3498db; }
    .log-worker { border-left: 3px solid #e94560; }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
    }
    
    .badge-pending { background: #6c757d; color: white; }
    .badge-progress { background: #ffc107; color: black; }
    .badge-complete { background: #28a745; color: white; }
    .badge-failed { background: #dc3545; color: white; }
    
    /* Progress section */
    .progress-section {
        background: rgba(255,255,255,0.02);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
    }
    
    /* Metrics */
    .metric-card {
        background: linear-gradient(135deg, #e94560 0%, #0f3460 100%);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = None
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    if 'current_plan' not in st.session_state:
        st.session_state.current_plan = None
    if 'current_report' not in st.session_state:
        st.session_state.current_report = None
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []


def render_header():
    """Render the app header."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("# 🔬 Multi-Agent Research Assistant")
        st.markdown("*Autonomous research powered by AI agents*")
    
    with col2:
        st.markdown("### Agent Status")
        if st.session_state.is_running:
            st.markdown("🟢 **Active**")
        else:
            st.markdown("⚪ **Idle**")


def render_sidebar():
    """Render the sidebar with controls."""
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")
        st.markdown("---")
        
        # Topic input
        topic = st.text_area(
            "📝 Research Topic",
            placeholder="Enter your research topic...\n\nExample: Sentiment analysis applications in social media",
            height=100
        )
        
        st.markdown("---")
        
        # Settings
        st.markdown("### ⚙️ Settings")
        
        show_logs = st.checkbox("Show detailed logs", value=True)
        auto_scroll = st.checkbox("Auto-scroll logs", value=True)
        
        st.markdown("---")
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            start_btn = st.button(
                "🚀 Start Research",
                use_container_width=True,
                disabled=st.session_state.is_running or not topic
            )
        
        with col2:
            clear_btn = st.button(
                "🗑️ Clear",
                use_container_width=True,
                disabled=st.session_state.is_running
            )
        
        st.markdown("---")
        
        # Info
        st.markdown("### 📊 Agent Architecture")
        st.markdown("""
        **Planner Agent** 🧠
        - Creates research plan
        - Defines tasks
        
        **Worker Agent** ⚡
        - Collects data
        - Analyzes content
        - Writes report
        - Self-reviews
        """)
        
        return topic, start_btn, clear_btn, show_logs, auto_scroll


def render_task_status(tasks):
    """Render the task status panel."""
    st.markdown("### 📋 Task Progress")
    
    for task in tasks:
        status_class = {
            "pending": "task-pending",
            "in_progress": "task-progress", 
            "completed": "task-complete",
            "failed": "task-failed"
        }.get(task.status.value, "task-pending")
        
        status_icon = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "failed": "❌"
        }.get(task.status.value, "⏳")
        
        st.markdown(f"""
        <div class="task-card {status_class}">
            <strong>{status_icon} Task {task.id}: {task.name}</strong>
            <br><small>{task.description[:100]}...</small>
        </div>
        """, unsafe_allow_html=True)


def render_logs(logs, auto_scroll=True):
    """Render the log panel."""
    st.markdown("### 📜 Agent Logs")
    
    log_container = st.container()
    
    with log_container:
        for entry in logs[-50:]:  # Show last 50 logs
            agent_class = "log-planner" if entry.agent.value == "planner" else "log-worker"
            agent_emoji = "🧠" if entry.agent.value == "planner" else "⚡"
            
            st.markdown(f"""
            <div class="log-entry {agent_class}">
                <span style="color: #888;">{entry.timestamp.strftime('%H:%M:%S')}</span>
                {agent_emoji} <strong>[{entry.agent.value.upper()}]</strong> 
                <span style="color: #e94560;">{entry.action}</span>: {entry.message}
            </div>
            """, unsafe_allow_html=True)


def render_report(report):
    """Render the final report."""
    st.markdown("## 📄 Research Report")
    
    # Report header
    st.markdown(f"### {report.title}")
    st.markdown(f"*Generated: {report.created_at.strftime('%Y-%m-%d %H:%M')}*")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Report", "📊 Analysis", "🔗 Sources", "📁 Download"])
    
    with tab1:
        for section_name, content in report.sections.items():
            with st.expander(f"📌 {section_name}", expanded=True):
                st.markdown(content)
    
    with tab2:
        if report.analysis:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Words Analyzed", f"{report.analysis.word_count:,}")
            with col2:
                st.metric("Sentences", f"{report.analysis.sentence_count:,}")
            with col3:
                st.metric("Avg. Sentence Length", f"{report.analysis.avg_sentence_length}")
            with col4:
                sentiment_color = {
                    "positive": "🟢",
                    "negative": "🔴",
                    "neutral": "🟡"
                }.get(report.analysis.sentiment_label, "⚪")
                st.metric("Sentiment", f"{sentiment_color} {report.analysis.sentiment_label.title()}")
            
            st.markdown("---")
            
            # Display charts
            st.markdown("### 📈 Visualizations")
            
            chart_cols = st.columns(len(report.analysis.chart_paths) if report.analysis.chart_paths else 1)
            
            for i, path in enumerate(report.analysis.chart_paths):
                if Path(path).exists():
                    with chart_cols[i % len(chart_cols)]:
                        st.image(path)
            
            # Keywords
            st.markdown("### 🔑 Top Keywords")
            keywords_df = {
                "Keyword": list(report.analysis.top_keywords.keys())[:10],
                "Frequency": list(report.analysis.top_keywords.values())[:10]
            }
            st.bar_chart(keywords_df, x="Keyword", y="Frequency")
    
    with tab3:
        st.markdown("### 🔗 Sources Used")
        for i, source in enumerate(report.sources, 1):
            st.markdown(f"""
            **{i}. {source.title}**  
            🔗 [{source.url[:60]}...]({source.url})  
            > {source.snippet[:200]}...
            """)
            st.markdown("---")
    
    with tab4:
        st.markdown("### 📥 Download Report")
        
        # Markdown download
        if report.markdown_content:
            st.download_button(
                label="📄 Download Markdown",
                data=report.markdown_content,
                file_name=f"research_report_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
        
        # Check for generated files
        output_dir = Path("outputs")
        if output_dir.exists():
            html_files = list(output_dir.glob("*.html"))
            if html_files:
                latest_html = max(html_files, key=lambda x: x.stat().st_mtime)
                with open(latest_html, 'r') as f:
                    st.download_button(
                        label="🌐 Download HTML",
                        data=f.read(),
                        file_name=f"research_report_{datetime.now().strftime('%Y%m%d')}.html",
                        mime="text/html"
                    )


def run_research(topic):
    """Execute the research workflow."""
    from orchestrator import ResearchOrchestrator
    
    # Create log callback that updates session state
    def log_callback(entry):
        st.session_state.logs.append(entry)
    
    # Create task callback
    def task_callback(task):
        # Update task in session state
        for i, t in enumerate(st.session_state.tasks):
            if t.id == task.id:
                st.session_state.tasks[i] = task
                break
    
    # Initialize orchestrator
    orchestrator = ResearchOrchestrator(
        log_callback=log_callback,
        task_callback=task_callback
    )
    
    st.session_state.orchestrator = orchestrator
    st.session_state.is_running = True
    st.session_state.logs = []
    
    try:
        # Run research
        report = orchestrator.run_research(topic)
        st.session_state.current_report = report
        st.session_state.current_plan = orchestrator.get_plan()
        st.session_state.tasks = orchestrator.get_plan().tasks
        
    except Exception as e:
        st.error(f"Research failed: {str(e)}")
        
    finally:
        st.session_state.is_running = False


def main():
    """Main application entry point."""
    init_session_state()
    render_header()
    
    # Sidebar
    topic, start_btn, clear_btn, show_logs, auto_scroll = render_sidebar()
    
    # Handle button clicks
    if clear_btn:
        st.session_state.logs = []
        st.session_state.current_plan = None
        st.session_state.current_report = None
        st.session_state.tasks = []
        st.session_state.is_running = False
        st.rerun()
    
    if start_btn and topic:
        with st.spinner("🔬 Research in progress..."):
            run_research(topic)
        st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Show report if available
        if st.session_state.current_report:
            render_report(st.session_state.current_report)
        else:
            # Welcome message
            st.markdown("""
            ## 👋 Welcome!
            
            This is a **Multi-Agent Research Assistant** that autonomously:
            
            1. 🔍 **Searches** for relevant sources
            2. 📥 **Collects** content from the web
            3. 📊 **Analyzes** text statistics and sentiment
            4. ✍️ **Writes** a comprehensive report
            5. 🔄 **Reviews** and improves the draft
            6. 📄 **Produces** the final formatted output
            
            ---
            
            ### 🚀 Getting Started
            
            1. Enter your research topic in the sidebar
            2. Click **Start Research**
            3. Watch the agents work!
            
            ---
            
            ### 🏗️ Architecture
            
            ```
            ┌─────────────────┐
            │  Planner Agent  │ → Creates research plan
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  Worker Agent   │ → Executes all tasks
            │                 │
            │  ├─ Collector   │ → Gathers sources
            │  ├─ Analyzer    │ → Analyzes content
            │  ├─ Writer      │ → Drafts report
            │  └─ Reviewer    │ → Self-improves
            └─────────────────┘
            ```
            """)
    
    with col2:
        # Task status
        if st.session_state.tasks:
            render_task_status(st.session_state.tasks)
        
        # Logs
        if show_logs and st.session_state.logs:
            render_logs(st.session_state.logs, auto_scroll)


if __name__ == "__main__":
    main()
