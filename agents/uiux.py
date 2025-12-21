"""
UI/UX Engineer Agent for Jarvis
Specializes in user experience, interface design, usability.
"""
from .base_agent import BaseAgent


class UIUXEngineer(BaseAgent):
    """UI/UX specialist for design systems and user experience."""
    
    def __init__(self):
        super().__init__("uiux")
    
    def _get_system_prompt(self) -> str:
        return """You are a Senior UI/UX Engineer.

EXPERTISE:
- User experience design
- Interface design and prototyping
- Design systems and component libraries
- Micro-interactions and animations
- Accessibility (WCAG 2.1)
- Responsive design
- User research synthesis

DESIGN PRINCIPLES:
- User-centered design
- Consistency and standards
- Error prevention
- Recognition over recall
- Flexibility and efficiency
- Aesthetic and minimal design

TOOLS & OUTPUT:
- Figma-ready specifications
- CSS implementations
- Component behavior specs
- Motion/animation specs
- Accessibility requirements
- Usability heuristics

Focus on practical, implementable designs."""
    
    def design_component(self, component: str, context: str = None) -> str:
        """Design a UI component with full specs."""
        prompt = f"""Design UI component:

COMPONENT: {component}
CONTEXT: {context or 'Web application'}

Output:
1. Visual specification (states, sizes, colors)
2. Behavior specification (interactions, transitions)
3. Accessibility requirements
4. CSS implementation (dark theme)
5. Animation specs (timing, easing)"""
        return self._call_llm(prompt)
    
    def create_design_system(self, brand: str) -> str:
        """Create a design system specification."""
        prompt = f"""Create a design system for: {brand}

Include:
## Color Palette (with CSS variables)
## Typography Scale
## Spacing System
## Component Library (buttons, inputs, cards, etc.)
## Icons and Imagery Guidelines
## Motion Principles
## Accessibility Standards

Output implementable CSS and specs."""
        return self._call_llm(prompt)
    
    def ux_audit(self, description: str) -> str:
        """Audit UX and provide recommendations."""
        prompt = f"""UX audit for:

{description}

Analyze using Nielsen's heuristics:
1. Visibility of system status
2. Match between system and real world
3. User control and freedom
4. Consistency and standards
5. Error prevention
6. Recognition over recall
7. Flexibility and efficiency
8. Aesthetic and minimal design
9. Help users recognize and recover from errors
10. Help and documentation

Provide specific recommendations."""
        return self._call_llm(prompt)
    
    def design_flow(self, task: str) -> str:
        """Design user flow for a feature."""
        prompt = f"""Design user flow for:

{task}

Include:
- Entry points
- Step-by-step flow (mermaid diagram)
- Decision points
- Error states and recovery
- Success states
- Microinteractions at each step"""
        return self._call_llm(prompt)
    
    def run(self, task: str) -> str:
        """Execute UI/UX task."""
        task_lower = task.lower()
        if "component" in task_lower:
            return self.design_component(task)
        elif "design system" in task_lower or "style guide" in task_lower:
            return self.create_design_system(task)
        elif "audit" in task_lower or "review" in task_lower:
            return self.ux_audit(task)
        elif "flow" in task_lower or "journey" in task_lower:
            return self.design_flow(task)
        else:
            return self._call_llm(f"UI/UX task: {task}")


# Singleton
uiux = UIUXEngineer()
