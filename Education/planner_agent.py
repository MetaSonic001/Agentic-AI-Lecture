"""
Agno Agent Definitions for Multi-Agent Research System.
Uses Agno (formerly Phidata) framework for proper multi-agent orchestration.
"""
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.function import Function
from config import GROQ_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from tools import (
    search_web,
    extract_webpage_content,
    analyze_text_statistics,
    analyze_sentiment,
    create_visualization
)
from logger_setup import log
import json


# --- Tool wrappers: ensure agent tool calls always accept null/missing args
# and return a JSON string as content (avoids Groq 'content missing' errors).
def _safe_search_web(*args, **kwargs):
    try:
        # Accept either positional or kw arg 'query'. Support cases where the
        # model passes a dict or a JSON-string containing the args.
        query = None
        if 'query' in kwargs:
            query = kwargs.get('query')
        elif args:
            query = args[0]

        # If query comes as a dict (function-call style), extract possible fields
        if isinstance(query, dict):
            # Commonly the model may include 'query' key inside
            query = query.get('query') or query.get('q') or ''

        # If the model passed a JSON string, try to parse
        if isinstance(query, str):
            s = query.strip()
            # remove wrapping quotes if present
            if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
                s = s[1:-1]
            # unescape common escaped quotes
            s = s.replace('\\"', '"').replace("\\'", "'")
            query = s

        # Fallback empty query
        if not query:
            query = ''

        result = search_web(query)
        content = result if isinstance(result, str) else json.dumps(result)
        return content
    except Exception as e:
        log.error(f"search_web tool error: {e}")
        return json.dumps({"error": str(e)})


def _safe_extract_webpage_content(*args, **kwargs):
    try:
        # Accept url either as kwarg or first positional arg
        url = None
        if 'url' in kwargs:
            url = kwargs.get('url')
        elif args:
            url = args[0]

        # If the model passed a dict, extract url key
        if isinstance(url, dict):
            url = url.get('url') or url.get('href') or url.get('link') or ''

        # If url is JSON string, sanitize
        if isinstance(url, str):
            s = url.strip()
            # remove wrapping quotes
            if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
                s = s[1:-1]
            # unescape
            s = s.replace('\\"', '"').replace("\\'", "'")
            # remove stray trailing backslashes
            while s.endswith('\\'):
                s = s[:-1]
            url = s

        if not url:
            url = ''

        result = extract_webpage_content(url)
        content = result if isinstance(result, str) else json.dumps(result)
        return content
    except Exception as e:
        log.error(f"extract_webpage_content tool error: {e}")
        return json.dumps({"error": str(e)})


def _safe_analyze_text_statistics(*args, **kwargs):
    try:
        text = kwargs.get('text') if 'text' in kwargs else (args[0] if args else "")
        if isinstance(text, str):
            text = text.strip()
            # If the text is a JSON blob from extract_webpage_content, extract the 'content' field
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict) and 'content' in parsed:
                    text = parsed.get('content', '')
            except Exception:
                pass
        # Enforce a maximum length to avoid function-call failures on very large payloads
        try:
            MAX_CHARS = 20000
            if isinstance(text, str) and len(text) > MAX_CHARS:
                text = text[:MAX_CHARS]
        except Exception:
            pass
        result = analyze_text_statistics(text)
        content = result if isinstance(result, str) else json.dumps(result)
        return content
    except Exception as e:
        log.error(f"analyze_text_statistics tool error: {e}")
        return json.dumps({"error": str(e)})


def _safe_analyze_sentiment(*args, **kwargs):
    try:
        text = kwargs.get('text') if 'text' in kwargs else (args[0] if args else "")
        if isinstance(text, str):
            text = text.strip()
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict) and 'content' in parsed:
                    text = parsed.get('content', '')
            except Exception:
                pass
        # Truncate very long text
        try:
            MAX_CHARS_SENT = 10000
            if isinstance(text, str) and len(text) > MAX_CHARS_SENT:
                text = text[:MAX_CHARS_SENT]
        except Exception:
            pass
        result = analyze_sentiment(text)
        content = result if isinstance(result, str) else json.dumps(result)
        return content
    except Exception as e:
        log.error(f"analyze_sentiment tool error: {e}")
        return json.dumps({"error": str(e)})


def _safe_create_visualization(*args, **kwargs):
    try:
        # Accept keywords or positional args: (keywords, sentiment, topic)
        if args and len(args) >= 3:
            keywords_arg, sentiment_arg, topic_arg = args[0], args[1], args[2]
        else:
            keywords_arg = kwargs.get('keywords')
            sentiment_arg = kwargs.get('sentiment')
            topic_arg = kwargs.get('topic', '')

        # Normalize inputs
        if isinstance(topic_arg, str):
            topic_arg = topic_arg.strip()

        # If analysis_results was passed as a JSON string, try to parse keywords and sentiment
        try:
            if isinstance(keywords_arg, str):
                parsed = json.loads(keywords_arg)
                # support either top_keywords or keyword list
                if isinstance(parsed, dict) and 'top_keywords' in parsed:
                    keywords_arg = parsed.get('top_keywords')
        except Exception:
            pass

        try:
            if isinstance(sentiment_arg, str):
                parsed_s = json.loads(sentiment_arg)
                if isinstance(parsed_s, dict) and 'score' in parsed_s:
                    sentiment_arg = parsed_s
        except Exception:
            pass

        result = create_visualization(keywords_arg or {}, sentiment_arg or {}, topic_arg or "")
        content = result if isinstance(result, str) else json.dumps(result)
        return content
    except Exception as e:
        log.error(f"create_visualization tool error: {e}")
        return json.dumps({"error": str(e)})



# Initialize the LLM
llm = Groq(
    id=LLM_MODEL,
    api_key=GROQ_API_KEY
)


def create_planner_agent() -> Agent:
    """
    Create the Planner Agent.
    
    Responsibilities:
    - Analyze the research topic
    - Break down into subtasks
    - Create structured research plan
    - Coordinate with Worker Agent
    """
    
    planner = Agent(
        name="Planner Agent",
        model=llm,
        role="Research Planning Expert",
        description=(
            "You are a strategic research planner. Your job is to analyze research topics "
            "and create comprehensive, actionable plans. You break down complex research "
            "questions into clear, sequential tasks."
        ),
        instructions=[
            "1. Carefully analyze the research topic provided by the user",
            "2. Identify key areas that need investigation",
            "3. Create a structured plan with 6 specific tasks:",
            "   - Task 1: Source Identification",
            "   - Task 2: Content Collection",
            "   - Task 3: Data Analysis",
            "   - Task 4: Report Drafting",
            "   - Task 5: Self-Review",
            "   - Task 6: Final Production",
            "4. For each task, provide clear, actionable descriptions",
            "5. Present the plan in a structured format",
            "6. Be specific about what needs to be accomplished in each task"
        ]
    )
    
    log.info("Planner Agent created")
    return planner


def create_worker_agent() -> Agent:
    """
    Create the Worker Agent.
    
    Responsibilities:
    - Search and collect sources
    - Extract and process content
    - Analyze text and sentiment
    - Write report sections
    - Review and improve content
    - Generate final outputs
    """
    
    # Define tools for the worker
    tools = [
        Function(
            name="search_web",
            description="Search the web using DuckDuckGo to find relevant sources",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "trustworthiness": {"type": "string"},
                    "source_filter": {"type": "string"}
                },
                "required": ["query"]
            },
            function=_safe_search_web
        ),
        Function(
            name="extract_webpage_content",
            description="Extract text content from a webpage URL",
            parameters={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "format": "uri"},
                    "trustworthiness": {"type": "string"}
                },
                "required": ["url"]
            },
            function=_safe_extract_webpage_content
        ),
        Function(
            name="analyze_text_statistics",
            description="Analyze text statistics including word count, keywords, etc.",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "analysis_type": {"type": "string", "enum": ["statistics", "sentiment"]}
                },
                "required": ["text"]
            },
            function=_safe_analyze_text_statistics
        ),
        Function(
            name="analyze_sentiment",
            description="Analyze the sentiment of text",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "analysis_type": {"type": "string", "enum": ["sentiment"]}
                },
                "required": ["text"]
            },
            function=_safe_analyze_sentiment
        ),
        Function(
            name="create_visualization",
            description="Create visualization charts from analysis results",
            parameters={
                "type": "object",
                "properties": {
                    "analysis_results": {"type": "string"},
                    "visualization_type": {"type": "string", "enum": ["chart", "wordcloud"]}
                },
                "required": ["analysis_results", "visualization_type"]
            },
            function=_safe_create_visualization
        )
    ]
    
    worker = Agent(
        name="Worker Agent",
        model=llm,
        role="Research Execution Specialist",
        description=(
            "You are an autonomous research worker. You execute research tasks end-to-end, "
            "from finding sources to producing final reports. You have tools to search the web, "
            "extract content, analyze data, and create visualizations."
        ),
        instructions=[
            "You will execute research tasks in sequence:",
            "",
            "TASK 1 - SOURCE IDENTIFICATION:",
            "- Use search_web tool to find 3-5 trustworthy sources",
            "- Look for authoritative, credible sources",
            "- Prioritize .edu, .org, government sites, and reputable publications",
            "",
            "TASK 2 - CONTENT COLLECTION:",
            "- Use extract_webpage_content tool on each source URL",
            "- Collect and store the extracted text",
            "- Note any extraction issues",
            "",
            "TASK 3 - DATA ANALYSIS:",
            "- Combine collected content",
            "- Use analyze_text_statistics tool to get word counts, keywords",
            "- Use analyze_sentiment tool to determine overall sentiment",
            "- Use create_visualization tool to generate charts",
            "",
            "TASK 4 - REPORT DRAFTING:",
            "- Write a comprehensive research report with these sections:",
            "  * Executive Summary (2-3 paragraphs)",
            "  * Introduction (context and significance)",
            "  * Key Findings (main discoveries from sources)",
            "  * Analysis (deeper interpretation)",
            "  * Conclusion (key takeaways)",
            "- Base content on collected sources",
            "- Be factual and cite findings",
            "",
            "TASK 5 - SELF-REVIEW:",
            "- Critically review your own draft",
            "- Identify areas for improvement",
            "- Rewrite sections to be clearer and more professional",
            "- Ensure logical flow and coherence",
            "",
            "TASK 6 - FINAL PRODUCTION:",
            "- Format the report in clean Markdown",
            "- Include source citations",
            "- Add analysis statistics",
            "- Reference visualization charts",
            "- Ensure professional presentation",
            "",
            "Execute each task thoroughly before moving to the next.",
            "Provide clear status updates as you work."
        ],
        tools=tools
    )
    
    log.info("Worker Agent created with tools")
    return worker


def create_team_agent() -> Agent:
    """
    Create a Team Agent that coordinates Planner and Worker.
    
    This is the orchestrator that manages the multi-agent workflow.
    """
    
    planner = create_planner_agent()
    worker = create_worker_agent()
    
    # Construct the coordinator agent without passing an unsupported `team` kwarg.
    team = Agent(
        name="Research Team Coordinator",
        model=llm,
        description=(
            "You coordinate a research team consisting of a Planner Agent and a Worker Agent. "
            "You delegate tasks appropriately and ensure smooth workflow."
        ),
        instructions=[
            "When given a research topic:",
            "1. First, ask the Planner Agent to create a research plan",
            "2. Review the plan",
            "3. Then, instruct the Worker Agent to execute the plan step-by-step",
            "4. Monitor progress and provide updates",
            "5. Ensure all tasks are completed successfully",
            "6. Present the final research report to the user",
            "",
            "Coordinate effectively between agents.",
            "Provide clear status updates at each phase."
        ]
    )

    # Attach the planner and worker as attributes so callers can access them if needed.
    setattr(team, "team_members", [planner, worker])
    
    log.info("Team Agent created with Planner and Worker")
    return team