# Jarvis v2 Agents Package

from .config import LM_STUDIO_URL, WORKSPACE_DIR, CONTEXT_DIR
from .context_manager import context
from .router import router
from .research import researcher
from .coder import coder
from .ops import ops
from .orchestrator import orchestrator
from .personality import get_chat_prompt, get_tool_prompt, format_for_voice, JARVIS_PERSONA, VOICE_PERSONA, clean_response
from .notifications import notify, notify_task_complete, notify_research_complete, notify_deployment_complete
from .brute_research import brute_researcher
from .synthesis import synthesizer, deep_research_v2
from .queue import task_queue, queue_autonomous, queue_research, get_queue_status
from .worker import start_queue_worker, stop_queue_worker
from .recycler import recycler, ContextRecycler
from .autonomous import autonomous_executor, AutonomousExecutor
from .project_manager import project_manager, ProjectManager, STACK_TEMPLATES
from .qa import qa_agent, QAAgent
from .terminal import terminal, TerminalAgent
from .code_indexer import code_indexer, CodeIndexer
from .code_reviewer import code_reviewer, CodeReviewer
from .browser_tester import browser_tester, BrowserTester
from .design_creativity import design_creativity, DesignCreativity
from .git_agent import git_agent, GitAgent

__all__ = [
    "context",
    "router",
    "researcher", 
    "coder",
    "ops",
    "orchestrator",
    "get_chat_prompt",
    "get_tool_prompt",
    "format_for_voice",
    "clean_response",
    "notify",
    "notify_task_complete",
    "brute_researcher",
    "synthesizer",
    "deep_research_v2",
    "task_queue",
    "queue_autonomous",
    "queue_research",
    "get_queue_status",
    "start_queue_worker",
    "stop_queue_worker",
    "recycler",
    "ContextRecycler",
    "autonomous_executor",
    "AutonomousExecutor",
    "project_manager",
    "ProjectManager",
    "STACK_TEMPLATES",
    "qa_agent",
    "QAAgent",
    "terminal",
    "TerminalAgent",
    "code_indexer",
    "CodeIndexer",
    "code_reviewer",
    "CodeReviewer",
    "browser_tester",
    "BrowserTester",
    "design_creativity",
    "DesignCreativity",
    "git_agent",
    "GitAgent",
]
