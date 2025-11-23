"""
Research Orchestrator using Agno Multi-Agent System.
Agno (formerly Phidata) provides lightweight multi-agent orchestration.
"""
from typing import Callable, Dict, Any
from datetime import datetime
from pathlib import Path
from agents import create_team_agent, create_planner_agent, create_worker_agent
from logger_setup import log
from config import OUTPUT_DIR


class ResearchOrchestrator:
    """
    Orchestrates the multi-agent research workflow using Phidata/Agno.
    """
    
    def __init__(self, status_callback: Callable = None):
        """
        Initialize the orchestrator.
        
        Args:
            status_callback: Function to call with status updates
        """
        self.status_callback = status_callback
        
        # Create output directories
        Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        Path(f"{OUTPUT_DIR}/charts").mkdir(parents=True, exist_ok=True)
        
        # Initialize agents
        log.info("Initializing multi-agent system...")
        self.team_agent = create_team_agent()
        
        # State tracking
        self.current_topic = None
        self.research_plan = None
        self.final_report = None
        self.task_status = []
        
        log.info("Research Orchestrator initialized")
    
    def _update_status(self, phase: str, message: str, details: Dict[str, Any] = None):
        """
        Update status and notify callback.
        
        Args:
            phase: Current phase name
            message: Status message
            details: Additional details
        """
        status = {
            "timestamp": datetime.now(),
            "phase": phase,
            "message": message,
            "details": details or {}
        }
        
        log.info(f"[{phase}] {message}")
        
        if self.status_callback:
            self.status_callback(status)
    
    def run_research(self, topic: str) -> Dict[str, Any]:
        """
        Execute the complete research workflow.
        
        Args:
            topic: Research topic
            
        Returns:
            Dictionary with research results
        """
        self.current_topic = topic
        log.info(f"Starting research on: {topic}")
        
        try:
            # Phase 1: Planning
            self._update_status(
                "PLANNING",
                "Analyzing topic and creating research plan...",
                {"topic": topic}
            )
            
            plan_prompt = f"""
Create a detailed research plan for the following topic:

TOPIC: {topic}

Break it down into 6 specific tasks with clear objectives for each task.
"""
            
            # Get planner agent separately for planning phase
            planner = create_planner_agent()
            plan_response = planner.run(plan_prompt)
            
            self.research_plan = plan_response.content
            
            self._update_status(
                "PLAN_CREATED",
                "Research plan created successfully",
                {"plan": self.research_plan}
            )
            
            # Phase 2: Execution
            self._update_status(
                "EXECUTION_START",
                "Worker Agent beginning task execution...",
                {}
            )
            
            execution_prompt = f"""
Execute a comprehensive research project on this topic:

TOPIC: {topic}

RESEARCH PLAN:
{self.research_plan}

Execute each task in sequence:
1. Search for 3 trustworthy sources using the search_web tool
2. Extract content from each source using extract_webpage_content tool
3. Analyze the collected content (statistics and sentiment)
4. Draft a comprehensive research report with all sections
5. Review and improve the draft
6. Format the final report in Markdown with citations and analysis

Provide detailed updates as you complete each task.
"""
            
            # Get worker agent for execution
            worker = create_worker_agent()
            execution_response = worker.run(execution_prompt)
            
            self.final_report = execution_response.content
            
            self._update_status(
                "EXECUTION_COMPLETE",
                "All tasks completed successfully!",
                {}
            )
            
            # Save report
            report_path = self._save_report(self.final_report)
            
            self._update_status(
                "REPORT_SAVED",
                f"Report saved to {report_path}",
                {"path": report_path}
            )
            
            result = {
                "success": True,
                "topic": topic,
                "plan": self.research_plan,
                "report": self.final_report,
                "report_path": report_path,
                "timestamp": datetime.now()
            }
            
            log.info("Research workflow completed successfully")
            return result
            
        except Exception as e:
            log.error(f"Research workflow failed: {str(e)}")
            self._update_status(
                "ERROR",
                f"Research failed: {str(e)}",
                {"error": str(e)}
            )
            
            return {
                "success": False,
                "topic": topic,
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    def _save_report(self, report_content: str) -> str:
        """
        Save the research report to a file.
        
        Args:
            report_content: Markdown report content
            
        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{OUTPUT_DIR}/research_report_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        log.info(f"Report saved: {filename}")
        return filename
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        return {
            "topic": self.current_topic,
            "has_plan": self.research_plan is not None,
            "has_report": self.final_report is not None
        }