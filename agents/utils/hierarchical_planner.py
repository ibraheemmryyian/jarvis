"""
Hierarchical Planner for Jarvis
Breaks down mega-tasks into sub-projects with dependencies.
"""
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class ProjectStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass
class SubProject:
    name: str
    description: str
    steps: List[str]
    depends_on: List[str]
    status: ProjectStatus = ProjectStatus.PENDING
    completed_steps: List[str] = None
    progress_percent: float = 0.0
    
    def __post_init__(self):
        if self.completed_steps is None:
            self.completed_steps = []


@dataclass
class HierarchicalPlan:
    main_goal: str
    sub_projects: List[SubProject]
    created_at: str
    current_sub_project: int = 0
    overall_progress: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "main_goal": self.main_goal,
            "sub_projects": [
                {
                    "name": sp.name,
                    "description": sp.description,
                    "steps": sp.steps,
                    "depends_on": sp.depends_on,
                    "status": sp.status.value,
                    "completed_steps": sp.completed_steps,
                    "progress_percent": sp.progress_percent
                }
                for sp in self.sub_projects
            ],
            "created_at": self.created_at,
            "current_sub_project": self.current_sub_project,
            "overall_progress": self.overall_progress
        }


class HierarchicalPlanner:
    """
    Breaks large objectives into manageable sub-projects.
    
    For tasks with 50+ estimated steps, this creates a hierarchy:
    - Main Goal
      - Sub-Project 1 (depends_on: [])
        - Step 1.1
        - Step 1.2
      - Sub-Project 2 (depends_on: [Sub-Project 1])
        - Step 2.1
    """
    
    # Threshold for considering a task "mega"
    MEGA_TASK_KEYWORDS = [
        "os", "system", "platform", "ecosystem", "full", "complete",
        "entire", "everything", "crm", "dashboard", "application",
        "business", "enterprise", "management", "saas", "marketplace"
    ]
    
    def is_mega_task(self, objective: str) -> bool:
        """Determine if objective is complex enough for hierarchical planning."""
        obj_lower = objective.lower()
        
        # Check for mega keywords
        keyword_match = any(kw in obj_lower for kw in self.MEGA_TASK_KEYWORDS)
        
        # Check for multiple components mentioned
        component_words = ["and", "with", "including", "plus", "also", ","]
        component_count = sum(1 for w in component_words if w in obj_lower)
        
        return keyword_match or component_count >= 2
    
    def create_hierarchical_plan(self, objective: str, llm_callback) -> HierarchicalPlan:
        """
        V4.3: Create a hierarchical plan that PRESERVES user intent.
        
        Args:
            objective: The main goal
            llm_callback: Function to call LLM with a prompt
        
        Returns:
            HierarchicalPlan with sub-projects
        """
        # V4.3: COFOUNDER MODE - Preserve intent, don't add features
        prompt = f"""Break down this objective into focused sub-projects.

OBJECTIVE: {objective}

CRITICAL RULES:
1. ONLY include tasks that directly serve the objective
2. DO NOT add generic features (auth, database, API) unless explicitly mentioned
3. FOCUS on what the user actually asked for
4. Keep steps specific to the actual goal

Return a JSON object:
{{
  "sub_projects": [
    {{
      "name": "Short descriptive name",
      "description": "What this accomplishes toward the objective",
      "steps": ["Specific step 1", "Specific step 2"],
      "depends_on": []
    }}
  ]
}}

Return ONLY valid JSON, no explanation."""

        try:
            response = llm_callback(prompt)
            
            # Parse JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                data = json.loads(response[json_start:json_end])
                
                sub_projects = []
                for sp_data in data.get("sub_projects", []):
                    sub_projects.append(SubProject(
                        name=sp_data["name"],
                        description=sp_data.get("description", ""),
                        steps=sp_data.get("steps", []),
                        depends_on=sp_data.get("depends_on", [])
                    ))
                
                return HierarchicalPlan(
                    main_goal=objective,
                    sub_projects=sub_projects,
                    created_at=datetime.now().isoformat()
                )
        except Exception as e:
            print(f"[HierarchicalPlanner] Failed to parse: {e}")
        
        # Fallback: single sub-project with basic steps
        return self._create_fallback_plan(objective)
    
    def _create_fallback_plan(self, objective: str) -> HierarchicalPlan:
        """Create a simple fallback plan if LLM parsing fails."""
        return HierarchicalPlan(
            main_goal=objective,
            sub_projects=[
                SubProject(
                    name="Main Project",
                    description=objective,
                    steps=[
                        "Analyze requirements",
                        "Design architecture",
                        "Implement core features",
                        "Add supporting features",
                        "Test and refine"
                    ],
                    depends_on=[]
                )
            ],
            created_at=datetime.now().isoformat()
        )
    
    def get_next_sub_project(self, plan: HierarchicalPlan) -> Optional[SubProject]:
        """Get the next sub-project that can be executed."""
        for sp in plan.sub_projects:
            if sp.status == ProjectStatus.PENDING:
                # Check if dependencies are met
                deps_met = all(
                    self._is_completed(plan, dep)
                    for dep in sp.depends_on
                )
                if deps_met:
                    return sp
        
        return None
    
    def _is_completed(self, plan: HierarchicalPlan, sub_project_name: str) -> bool:
        """Check if a sub-project is completed."""
        for sp in plan.sub_projects:
            if sp.name == sub_project_name:
                return sp.status == ProjectStatus.COMPLETED
        return False
    
    def mark_step_complete(self, plan: HierarchicalPlan, sub_project_name: str, step: str):
        """Mark a step as completed in a sub-project."""
        for sp in plan.sub_projects:
            if sp.name == sub_project_name:
                if step not in sp.completed_steps:
                    sp.completed_steps.append(step)
                
                # Update progress
                if sp.steps:
                    sp.progress_percent = len(sp.completed_steps) / len(sp.steps) * 100
                
                # Mark complete if all steps done
                if len(sp.completed_steps) >= len(sp.steps):
                    sp.status = ProjectStatus.COMPLETED
                elif sp.status == ProjectStatus.PENDING:
                    sp.status = ProjectStatus.IN_PROGRESS
                
                break
        
        # Update overall progress
        self._update_overall_progress(plan)
    
    def _update_overall_progress(self, plan: HierarchicalPlan):
        """Update overall plan progress."""
        if not plan.sub_projects:
            return
        
        total_steps = sum(len(sp.steps) for sp in plan.sub_projects)
        completed_steps = sum(len(sp.completed_steps) for sp in plan.sub_projects)
        
        if total_steps > 0:
            plan.overall_progress = completed_steps / total_steps * 100
    
    def get_progress_display(self, plan: HierarchicalPlan) -> str:
        """Get a formatted progress display."""
        lines = [
            f"## {plan.main_goal}",
            f"Overall: {plan.overall_progress:.0f}%",
            ""
        ]
        
        for i, sp in enumerate(plan.sub_projects):
            status_icon = {
                ProjectStatus.PENDING: "⬜",
                ProjectStatus.IN_PROGRESS: "🔄",
                ProjectStatus.COMPLETED: "✅",
                ProjectStatus.BLOCKED: "🚫",
                ProjectStatus.FAILED: "❌"
            }.get(sp.status, "⬜")
            
            lines.append(f"{status_icon} {sp.name} ({sp.progress_percent:.0f}%)")
            
            if sp.status == ProjectStatus.IN_PROGRESS:
                for step in sp.steps:
                    done = "✓" if step in sp.completed_steps else " "
                    lines.append(f"   [{done}] {step[:50]}")
        
        return "\n".join(lines)


# Singleton
hierarchical_planner = HierarchicalPlanner()
