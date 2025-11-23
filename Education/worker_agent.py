"""
Worker Agent - Executes all research tasks autonomously.
Handles: Collection, Analysis, Writing, and Review.
"""
from datetime import datetime
from typing import List, Dict, Callable
from models import (
    Task, TaskStatus, ResearchPlan, ResearchReport, 
    Source, AnalysisResult, AgentLog, AgentType
)
from llm_client import get_llm_client
from data_collector import DataCollector
from analyzer import TextAnalyzer
from report_generator import ReportGenerator
from config import MAX_SOURCES, MAX_REVIEW_ITERATIONS
from logger_setup import log


class WorkerAgent:
    """Agent that performs all research work autonomously."""
    
    def __init__(self, log_callback: Callable = None):
        self.llm = get_llm_client()
        self.collector = DataCollector()
        self.analyzer = TextAnalyzer()
        self.generator = ReportGenerator()
        self.log_callback = log_callback
        
        # State
        self.sources: List[Source] = []
        self.analysis: AnalysisResult = None
        self.report: ResearchReport = None
        
        log.info("WorkerAgent initialized")
    
    def _emit_log(self, action: str, message: str, details: dict = None):
        """Emit a log entry for the UI."""
        entry = AgentLog(
            timestamp=datetime.now(),
            agent=AgentType.WORKER,
            action=action,
            message=message,
            details=details
        )
        if self.log_callback:
            self.log_callback(entry)
        log.info(f"[WORKER] {action}: {message}")
    
    def execute_plan(self, plan: ResearchPlan, 
                    task_callback: Callable = None) -> ResearchReport:
        """Execute all tasks in the research plan."""
        self._emit_log("START", f"Beginning research on: {plan.topic}")
        
        for task in plan.tasks:
            try:
                task.status = TaskStatus.IN_PROGRESS
                task.started_at = datetime.now()
                
                if task_callback:
                    task_callback(task)
                
                self._emit_log("TASK_START", f"Starting: {task.name}")
                
                # Route to appropriate handler
                if task.id == 1:
                    result = self._task_identify_sources(plan.topic)
                elif task.id == 2:
                    result = self._task_collect_content()
                elif task.id == 3:
                    result = self._task_analyze(plan.topic)
                elif task.id == 4:
                    result = self._task_draft_report(plan.topic)
                elif task.id == 5:
                    result = self._task_review()
                elif task.id == 6:
                    result = self._task_finalize()
                else:
                    result = "Unknown task"
                
                task.status = TaskStatus.COMPLETED
                task.result = result
                task.completed_at = datetime.now()
                
                self._emit_log("TASK_COMPLETE", f"Completed: {task.name}")
                
                if task_callback:
                    task_callback(task)
                    
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.result = str(e)
                task.completed_at = datetime.now()
                self._emit_log("TASK_FAILED", f"Failed: {task.name} - {str(e)}")
                log.error(f"Task {task.id} failed: {e}")
        
        self._emit_log("COMPLETE", "Research completed!")
        return self.report
    
    def _task_identify_sources(self, topic: str) -> str:
        """Task 1: Identify trustworthy sources."""
        self._emit_log("SEARCH", f"Searching for sources on: {topic}")
        
        # Use LLM to create better search query
        prompt = f"""Create a focused search query to find authoritative sources about:
{topic}

Respond with just the search query, nothing else."""

        search_query = self.llm.generate(prompt, temperature=0.3).strip()
        self._emit_log("QUERY", f"Search query: {search_query}")
        
        # Search for sources
        self.sources = self.collector.search(search_query, MAX_SOURCES + 2)
        
        source_list = "\n".join([f"- {s.title}" for s in self.sources[:MAX_SOURCES]])
        return f"Found {len(self.sources)} sources:\n{source_list}"
    
    def _task_collect_content(self) -> str:
        """Task 2: Collect content from sources."""
        self._emit_log("COLLECT", f"Extracting content from {len(self.sources)} sources")
        
        collected = []
        for i, source in enumerate(self.sources[:MAX_SOURCES]):
            self._emit_log("EXTRACT", f"Extracting: {source.title[:50]}...")
            source = self.collector.extract_content(source)
            if source.content:
                collected.append(source)
        
        self.sources = collected
        total_chars = sum(len(s.content) for s in self.sources)
        return f"Collected {total_chars:,} characters from {len(self.sources)} sources"
    
    def _task_analyze(self, topic: str) -> str:
        """Task 3: Analyze collected content."""
        self._emit_log("ANALYZE", "Running text analysis...")
        
        self.analysis = self.analyzer.analyze(self.sources, topic)
        
        return (f"Analysis complete: {self.analysis.word_count:,} words, "
                f"sentiment: {self.analysis.sentiment_label}")
    
    def _task_draft_report(self, topic: str) -> str:
        """Task 4: Draft the research report."""
        self._emit_log("DRAFT", "Generating report sections...")
        
        # Prepare context
        source_context = "\n\n".join([
            f"SOURCE: {s.title}\n{s.content[:1500]}" 
            for s in self.sources
        ])
        
        analysis_context = f"""
ANALYSIS RESULTS:
- Words analyzed: {self.analysis.word_count}
- Sentiment: {self.analysis.sentiment_label} ({self.analysis.sentiment_score})
- Top keywords: {', '.join(list(self.analysis.top_keywords.keys())[:10])}
"""
        
        sections = {}
        section_prompts = {
            "Executive Summary": "Write a concise executive summary (2-3 paragraphs) of the research findings.",
            "Introduction": "Write an introduction explaining the topic and its significance.",
            "Key Findings": "Summarize the main findings from the sources in bullet points.",
            "Analysis": "Provide deeper analysis and interpretation of the findings.",
            "Conclusion": "Write a conclusion with key takeaways and potential future directions."
        }
        
        system_prompt = """You are a research report writer. Write clear, professional, 
and well-structured content based on the provided sources and analysis. 
Be factual and cite findings from the sources."""

        for section, instruction in section_prompts.items():
            self._emit_log("WRITING", f"Writing section: {section}")
            
            prompt = f"""Based on the following sources and analysis, {instruction}

TOPIC: {topic}

{source_context}

{analysis_context}

Write the {section} section:"""
            
            content = self.llm.generate(prompt, system_prompt, temperature=0.7)
            sections[section] = content.strip()
        
        # Create report object
        self.report = ResearchReport(
            title=f"Research Report: {topic}",
            topic=topic,
            sections=sections,
            sources=self.sources,
            analysis=self.analysis
        )
        
        return f"Drafted {len(sections)} sections"
    
    def _task_review(self) -> str:
        """Task 5: Self-review and improve the draft."""
        self._emit_log("REVIEW", "Starting self-review process...")
        
        system_prompt = """You are a critical editor reviewing a research report. 
Identify specific improvements needed and rewrite sections to be clearer, 
more professional, and better structured. Focus on clarity and accuracy."""

        improvements = 0
        
        for iteration in range(MAX_REVIEW_ITERATIONS):
            self._emit_log("REVIEW_ITERATION", f"Review iteration {iteration + 1}")
            
            for section_name, content in self.report.sections.items():
                prompt = f"""Review and improve this section of a research report on "{self.report.topic}".

SECTION: {section_name}
CURRENT CONTENT:
{content}

Provide an improved version that is:
1. Clearer and more concise
2. Better structured
3. More professional in tone
4. Factually accurate

Return ONLY the improved content, no explanations."""
                
                improved = self.llm.generate(prompt, system_prompt, temperature=0.5)
                
                if len(improved.strip()) > 50:  # Valid improvement
                    self.report.sections[section_name] = improved.strip()
                    improvements += 1
        
        return f"Completed {MAX_REVIEW_ITERATIONS} review iterations, {improvements} improvements"
    
    def _task_finalize(self) -> str:
        """Task 6: Generate final report outputs."""
        self._emit_log("FINALIZE", "Generating final outputs...")
        
        # Generate markdown
        self.generator.generate_markdown(self.report)
        md_path = self.generator.save_markdown(self.report)
        self._emit_log("OUTPUT", f"Saved markdown: {md_path}")
        
        # Generate HTML
        html_path = self.generator.save_html(self.report)
        self._emit_log("OUTPUT", f"Saved HTML: {html_path}")
        
        return f"Generated outputs: {md_path}, {html_path}"
