"""
Data models for the research assistant using dataclasses.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(Enum):
    PLANNER = "planner"
    WORKER = "worker"


@dataclass
class Task:
    """Represents a single task in the research plan."""
    id: int
    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Source:
    """Represents a research source."""
    url: str
    title: str
    snippet: str
    content: str = ""
    author: Optional[str] = None
    publisher: Optional[str] = None
    publish_date: Optional[str] = None
    doi: Optional[str] = None
    accessed_at: Optional[datetime] = None
    raw_path: Optional[str] = None
    relevance_score: float = 0.0


@dataclass
class AnalysisResult:
    """Results from text analysis."""
    word_count: int = 0
    sentence_count: int = 0
    avg_sentence_length: float = 0.0
    top_keywords: Dict[str, int] = field(default_factory=dict)
    sentiment_score: float = 0.0
    sentiment_label: str = "neutral"
    chart_paths: List[str] = field(default_factory=list)


@dataclass
class ResearchPlan:
    """The complete research plan from the Planner Agent."""
    topic: str
    tasks: List[Task] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResearchReport:
    """The final research report."""
    title: str
    topic: str
    sections: Dict[str, str] = field(default_factory=dict)
    # Contributors: list of agent names (e.g., Planner Agent, Worker Agent)
    contributors: List[str] = field(default_factory=list)
    # Map from section name -> contributor (agent that wrote/edited it)
    section_authors: Dict[str, str] = field(default_factory=dict)
    sources: List[Source] = field(default_factory=list)
    analysis: Optional[AnalysisResult] = None
    markdown_content: str = ""
    pdf_path: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentLog:
    """Log entry for agent actions."""
    timestamp: datetime
    agent: AgentType
    action: str
    message: str
    details: Optional[Dict] = None
