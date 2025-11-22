"""
Orchestrator - Coordinates the multi-agent research workflow.
"""
from typing import Callable, List
from models import ResearchPlan, ResearchReport, AgentLog, Task
from planner_agent import PlannerAgent
from worker_agent import WorkerAgent
from logger_setup import log


class ResearchOrchestrator:
    """Coordinates the Planner and Worker agents."""
    
    def __init__(self, log_callback: Callable = None, task_callback: Callable = None):
        self.log_callback = log_callback
        self.task_callback = task_callback
        self.logs: List[AgentLog] = []
        
        # Initialize agents with callbacks
        self.planner = PlannerAgent(log_callback=self._handle_log)
        self.worker = WorkerAgent(log_callback=self._handle_log)
        
        self.current_plan: ResearchPlan = None
        self.current_report: ResearchReport = None
        
        log.info("ResearchOrchestrator initialized")
    
    def _handle_log(self, entry: AgentLog):
        """Handle log entries from agents."""
        self.logs.append(entry)
        if self.log_callback:
            self.log_callback(entry)
    
    def run_research(self, topic: str) -> ResearchReport:
        """Execute the complete research workflow."""
        log.info(f"Starting research workflow for: {topic}")
        
        # Phase 1: Planning
        log.info("Phase 1: Creating research plan...")
        self.current_plan = self.planner.create_plan(topic)
        
        # Phase 2: Execution
        log.info("Phase 2: Executing research plan...")
        self.current_report = self.worker.execute_plan(
            self.current_plan,
            task_callback=self.task_callback
        )
        
        log.info("Research workflow complete!")
        return self.current_report
    
    def get_plan(self) -> ResearchPlan:
        """Get the current research plan."""
        return self.current_plan
    
    def get_report(self) -> ResearchReport:
        """Get the current research report."""
        return self.current_report
    
    def get_logs(self) -> List[AgentLog]:
        """Get all log entries."""
        return self.logs
    
    def clear(self):
        """Reset the orchestrator state."""
        self.logs = []
        self.current_plan = None
        self.current_report = None
        log.info("Orchestrator state cleared")
