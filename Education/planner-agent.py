"""
Planner Agent - Creates research plans and coordinates tasks.
"""
import json
import re
from datetime import datetime
from typing import List, Callable
from models import Task, TaskStatus, ResearchPlan, AgentLog, AgentType
from llm_client import get_llm_client
from logger_setup import log


class PlannerAgent:
    """Agent responsible for creating and managing research plans."""
    
    def __init__(self, log_callback: Callable = None):
        self.llm = get_llm_client()
        self.log_callback = log_callback
        log.info("PlannerAgent initialized")
    
    def _emit_log(self, action: str, message: str, details: dict = None):
        """Emit a log entry for the UI."""
        entry = AgentLog(
            timestamp=datetime.now(),
            agent=AgentType.PLANNER,
            action=action,
            message=message,
            details=details
        )
        if self.log_callback:
            self.log_callback(entry)
        log.info(f"[PLANNER] {action}: {message}")
    
    def create_plan(self, topic: str) -> ResearchPlan:
        """Create a research plan for the given topic."""
        self._emit_log("PLANNING", f"Creating research plan for: {topic}")
        
        system_prompt = """You are a Research Planning Agent. Your job is to create 
structured research plans. You must respond with a valid JSON array of tasks.

Each task should have:
- name: Short task name
- description: Detailed description of what to do

Create exactly 6 tasks for a mini research report:
1. Source Identification - Find trustworthy sources
2. Content Collection - Extract content from sources
3. Data Analysis - Analyze text statistics and sentiment
4. Report Drafting - Write the initial report sections
5. Self-Review - Critique and improve the draft
6. Final Production - Produce the final formatted report

Respond ONLY with a JSON array, no other text."""

        prompt = f"""Create a research plan for the following topic:

TOPIC: {topic}

Respond with a JSON array of 6 tasks. Example format:
[
  {{"name": "Source Identification", "description": "Find 3 trustworthy sources about..."}},
  ...
]"""

        try:
            response = self.llm.generate(prompt, system_prompt, temperature=0.3)
            
            # Extract JSON from response
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                tasks_data = json.loads(json_match.group())
            else:
                raise ValueError("No valid JSON found in response")
            
            # Create task objects
            tasks = []
            for i, t in enumerate(tasks_data):
                task = Task(
                    id=i + 1,
                    name=t.get("name", f"Task {i+1}"),
                    description=t.get("description", ""),
                    status=TaskStatus.PENDING
                )
                tasks.append(task)
                self._emit_log("TASK_CREATED", f"Task {i+1}: {task.name}")
            
            plan = ResearchPlan(topic=topic, tasks=tasks)
            
            self._emit_log("PLAN_COMPLETE", f"Created plan with {len(tasks)} tasks")
            return plan
            
        except Exception as e:
            log.error(f"Failed to create plan: {e}")
            # Fallback to default plan
            return self._create_default_plan(topic)
    
    def _create_default_plan(self, topic: str) -> ResearchPlan:
        """Create a default research plan if LLM fails."""
        self._emit_log("FALLBACK", "Using default research plan")
        
        default_tasks = [
            Task(1, "Source Identification", f"Find 3 trustworthy sources about {topic}"),
            Task(2, "Content Collection", "Extract and process content from identified sources"),
            Task(3, "Data Analysis", "Analyze text statistics, keywords, and sentiment"),
            Task(4, "Report Drafting", "Write initial report sections based on analysis"),
            Task(5, "Self-Review", "Critique the draft and identify improvements"),
            Task(6, "Final Production", "Produce the final formatted research report"),
        ]
        
        return ResearchPlan(topic=topic, tasks=default_tasks)
    
    def update_task_status(self, plan: ResearchPlan, task_id: int, 
                          status: TaskStatus, result: str = None):
        """Update the status of a task in the plan."""
        for task in plan.tasks:
            if task.id == task_id:
                task.status = status
                if result:
                    task.result = result
                if status == TaskStatus.IN_PROGRESS:
                    task.started_at = datetime.now()
                elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    task.completed_at = datetime.now()
                    
                self._emit_log(
                    "TASK_UPDATE",
                    f"Task {task_id} ({task.name}): {status.value}",
                    {"task_id": task_id, "status": status.value}
                )
                break
