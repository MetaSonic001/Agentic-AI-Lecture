"""
Streamlit UI for Multi-Agent Research Assistant using Agno.
Agno (formerly Phidata) - Lightweight multi-agent framework.
"""
import streamlit as st
from datetime import datetime
from pathlib import Path
import time
import os
import sys

# Ensure the Education package folder is discoverable for local imports
# when this file is run via `streamlit run` from various working directories.
sys.path.insert(0, os.path.dirname(__file__))

# Page config
st.set_page_config(
    page_title="Multi-Agent Research Assistant (Agno)",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    h1, h2, h3 { color: #e94560 !important; }
    
    .status-card {
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #e94560;
    }
    
    .phase-box {
        background: rgba(255,255,255,0.03);
        border-radius: 8px;
        padding: 15px;
        margin: 8px 0;
        border-left: 3px solid #3498db;
    }
    
    .success-box {
        background: rgba(40, 167, 69, 0.1);
        border-left: 3px solid #28a745;
    }
    
    .error-box {
        background: rgba(220, 53, 69, 0.1);
        border-left: 3px solid #dc3545;
    }
    
    .log-entry {
        font-family: 'Monaco', monospace;
        font-size: 0.85em;
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 6px;
        background: rgba(0,0,0,0.2);
        border-left: 3px solid #ffc107;
    }
    
    .agent-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
        margin: 5px;
    }
    
    .badge-planner { background: #3498db; color: white; }
    .badge-worker { background: #e94560; color: white; }
    .badge-team { background: #2ecc71; color: white; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state."""
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = None
    if 'status_log' not in st.session_state:
        st.session_state.status_log = []
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False


def render_header():
    """Render header."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("# 🔬 Multi-Agent Research Assistant")
        st.markdown("*Powered by **Agno** Multi-Agent Framework*")
    
    with col2:
        st.markdown("### System Status")
        if st.session_state.is_running:
            st.markdown("🟢 **Agents Active**")
        else:
            st.markdown("⚪ **Idle**")


def render_sidebar():
    """Render sidebar controls."""
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")
        st.markdown("---")
        
        # Topic input
        topic = st.text_area(
            "📝 Research Topic",
            placeholder="Enter your research topic...\n\nExamples:\n- Sentiment analysis applications\n- Quantum computing advances\n- Climate change mitigation strategies",
            height=120
        )
        
        st.markdown("---")
        
        # Agent info
        st.markdown("### 🤖 Active Agents")
        st.markdown('<span class="agent-badge badge-planner">🧠 Planner</span>', unsafe_allow_html=True)
        st.markdown('<span class="agent-badge badge-worker">⚡ Worker</span>', unsafe_allow_html=True)
        st.markdown('<span class="agent-badge badge-team">👥 Team Coordinator</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            start_btn = st.button(
                "🚀 Start Research",
                use_container_width=True,
                disabled=st.session_state.is_running or not topic,
                type="primary"
            )
        
        with col2:
            clear_btn = st.button(
                "🗑️ Clear",
                use_container_width=True,
                disabled=st.session_state.is_running
            )
        
        st.markdown("---")
        
        # Framework info
        st.markdown("### 📚 Framework")
        st.info("""
**Agno** (formerly Phidata)
- True multi-agent orchestration
- Tool-equipped agents
- Autonomous execution
- Built-in coordination
        """)
        
        st.markdown("### 🛠️ Agent Tools")
        st.markdown("""
- `search_web`: DuckDuckGo search
- `extract_webpage_content`: Web scraping
- `analyze_text_statistics`: Text analysis
- `analyze_sentiment`: Sentiment detection
- `create_visualization`: Chart generation
        """)
        
        return topic, start_btn, clear_btn


def render_status_log(status_log):
    """Render status updates."""
    st.markdown("### 📊 Research Progress")
    
    if not status_log:
        st.info("Waiting to start research...")
        return
    
    for status in status_log:
        phase = status.get('phase', 'UNKNOWN')
        message = status.get('message', '')
        timestamp = status.get('timestamp', datetime.now())
        
        # Determine styling
        if phase in ['EXECUTION_COMPLETE', 'REPORT_SAVED']:
            box_class = 'success-box'
            icon = '✅'
        elif phase == 'ERROR':
            box_class = 'error-box'
            icon = '❌'
        else:
            box_class = ''
            icon = '🔄'
        
        st.markdown(f"""
        <div class="phase-box {box_class}">
            <strong>{icon} {phase}</strong><br>
            <small>{timestamp.strftime('%H:%M:%S')}</small><br>
            {message}
        </div>
        """, unsafe_allow_html=True)


def render_research_plan(plan: str):
    """Render the research plan."""
    st.markdown("### 📋 Research Plan")
    with st.expander("View Plan", expanded=True):
        st.markdown(plan)


def render_final_report(report: str, report_path: str = None):
    """Render the final report."""
    st.markdown("### 📄 Final Research Report")
    
    tabs = st.tabs(["📝 Report", "📥 Download", "🖼️ Visualizations"])
    
    with tabs[0]:
        st.markdown(report)
    
    with tabs[1]:
        if report:
            st.download_button(
                label="📄 Download Markdown Report",
                data=report,
                file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        if report_path and Path(report_path).exists():
            st.success(f"Report also saved to: `{report_path}`")
    
    with tabs[2]:
        # Display any generated charts
        charts_dir = Path("outputs/charts")
        if charts_dir.exists():
            chart_files = list(charts_dir.glob("*.png"))
            if chart_files:
                st.markdown("#### Generated Visualizations")
                
                cols = st.columns(min(len(chart_files), 3))
                for i, chart_path in enumerate(chart_files):
                    with cols[i % len(cols)]:
                        st.image(str(chart_path), use_container_width=True)
            else:
                st.info("No visualizations generated yet.")
        else:
            st.info("Charts directory not found.")


def run_research_workflow(topic: str):
    """Execute the research workflow."""
    from orchestrator import ResearchOrchestrator
    
    # Status callback
    def status_callback(status):
        st.session_state.status_log.append(status)
    
    # Initialize orchestrator
    orchestrator = ResearchOrchestrator(status_callback=status_callback)
    st.session_state.orchestrator = orchestrator
    st.session_state.is_running = True
    st.session_state.status_log = []
    
    try:
        # Run research
        result = orchestrator.run_research(topic)
        st.session_state.result = result
        
    except Exception as e:
        st.error(f"Research failed: {str(e)}")
        st.session_state.result = {
            "success": False,
            "error": str(e)
        }
        
    finally:
        st.session_state.is_running = False


def main():
    """Main application."""
    init_session_state()
    render_header()
    
    # Sidebar
    topic, start_btn, clear_btn = render_sidebar()
    
    # Handle actions
    if clear_btn:
        st.session_state.status_log = []
        st.session_state.result = None
        st.session_state.is_running = False
        st.rerun()
    
    if start_btn and topic:
        with st.spinner("🤖 Agents are working..."):
            run_research_workflow(topic)
        st.rerun()
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Show results
        if st.session_state.result:
            result = st.session_state.result
            
            if result.get('success'):
                st.success("✅ Research Completed Successfully!")
                
                # Show plan
                if result.get('plan'):
                    render_research_plan(result['plan'])
                
                # Show report
                if result.get('report'):
                    render_final_report(
                        result['report'],
                        result.get('report_path')
                    )
            else:
                st.error(f"❌ Research Failed: {result.get('error')}")
        
        else:
            # Welcome screen
            st.markdown("""
            ## 👋 Welcome to Multi-Agent Research Assistant
            
            This system uses **Agno (formerly Phidata)** for true multi-agent orchestration.
            
            ### 🤖 Meet the Agents
            
            **🧠 Planner Agent**
            - Strategic research planning
            - Task breakdown and sequencing
            - Coordinates the research workflow
            
            **⚡ Worker Agent**
            - Equipped with 5 specialized tools
            - Autonomous task execution
            - Data collection, analysis, and writing
            - Self-review and improvement
            
            **👥 Team Coordinator**
            - Orchestrates agent collaboration
            - Manages handoffs between agents
            - Ensures workflow completion
            
            ---
            
            ### 🚀 How It Works
            
            1. **Planning Phase**: Planner Agent analyzes your topic and creates a 6-task plan
            2. **Execution Phase**: Worker Agent executes each task using its tools:
               - Searches web for sources
               - Extracts and processes content
               - Analyzes text statistics and sentiment
               - Drafts comprehensive report
               - Reviews and improves draft
               - Formats final output
            3. **Completion**: Receive a polished research report with visualizations
            
            ---
            
            ### 📊 Research Output
            
            - **Comprehensive Report**: Multi-section research document
            - **Statistical Analysis**: Word counts, keywords, sentiment
            - **Visualizations**: Keyword charts, word clouds, sentiment gauges
            - **Source Citations**: All sources properly referenced
            - **Downloadable**: Markdown format for easy sharing
            
            ---
            
            ### 🎯 Perfect For
            
            - Academic research summaries
            - Market analysis reports
            - Technology trend reviews
            - Literature surveys
            - Topic overviews
            
            **Get started by entering a topic in the sidebar!** 👈
            """)
    
    with col2:
        # Status log
        render_status_log(st.session_state.status_log)


if __name__ == "__main__":
    main()