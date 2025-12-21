"""
Frontend Developer Agent for Jarvis
Specializes in modern frontend: React, Vue, Next.js, CSS, animations.
"""
from .base_agent import BaseAgent


class FrontendDeveloper(BaseAgent):
    """Expert frontend engineer specializing in React and modern web."""
    
    def __init__(self):
        super().__init__("frontend_dev")
    
    def _get_system_prompt(self) -> str:
        return """You are an Expert Frontend Developer.

SPECIALTIES:
- React, Next.js, Vue 3, Svelte
- TypeScript, modern ES6+
- CSS-in-JS, Tailwind, vanilla CSS
- Animations (Framer Motion, GSAP, CSS transitions)
- State management (Redux, Zustand, Jotai)
- Component architecture and design systems

DESIGN PHILOSOPHY:
- Mobile-first responsive design
- Glassmorphism, gradients, subtle animations
- Dark mode default with CSS variables
- Accessible (ARIA, focus states)
- Performance (lazy loading, code splitting)

OUTPUT FORMAT:
For components, output COMPLETE code with:
1. Full JSX/TSX structure
2. Inline styles or CSS module
3. All props and types defined
4. Loading/error states
5. Responsive breakpoints

Always explain design choices briefly."""
    
    def create_component(self, description: str, framework: str = "react") -> str:
        """Create a complete frontend component."""
        prompt = f"""Create a production-ready {framework} component:

{description}

Requirements:
- Complete, self-contained code
- Dark theme with purple/cyan accents
- Smooth hover transitions
- Mobile responsive
- TypeScript if React/Next

Output the complete component code."""
        return self._call_llm(prompt)
    
    def create_page(self, description: str, framework: str = "react") -> str:
        """Create a complete page with all sections."""
        prompt = f"""Create a complete {framework} page:

{description}

Include:
- Header/navigation
- All content sections
- Footer
- Proper SEO head tags
- Animations on scroll
- Responsive design

Output the COMPLETE page code (500+ lines)."""
        return self._call_llm(prompt)
    
    def run(self, task: str) -> str:
        """Execute frontend development task."""
        if "component" in task.lower():
            return self.create_component(task)
        elif "page" in task.lower():
            return self.create_page(task)
        else:
            return self._call_llm(f"Frontend task: {task}")


# Singleton
frontend_dev = FrontendDeveloper()
