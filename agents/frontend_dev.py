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
    
    def run(self, task: str, project_context: str = "") -> str:
        """Execute frontend development task with proper file output."""
        task_lower = task.lower()
        
        # Detect what kind of file/component is needed
        if any(kw in task_lower for kw in ["hero", "header", "nav", "landing"]):
            file_hint = "HeroSection.jsx or Header.jsx"
        elif any(kw in task_lower for kw in ["form", "contact", "login", "signup"]):
            file_hint = "ContactForm.jsx or LoginForm.jsx"
        elif any(kw in task_lower for kw in ["card", "testimonial", "feature"]):
            file_hint = "FeatureCard.jsx or Testimonials.jsx"
        elif any(kw in task_lower for kw in ["footer"]):
            file_hint = "Footer.jsx"
        elif any(kw in task_lower for kw in ["dashboard", "admin"]):
            file_hint = "Dashboard.jsx"
        elif any(kw in task_lower for kw in ["css", "style", "theme", "dark mode"]):
            file_hint = "styles.css or theme.css"
        elif any(kw in task_lower for kw in ["animation", "scroll"]):
            file_hint = "animations.js or ScrollAnimations.jsx"
        else:
            file_hint = "App.jsx or index.jsx"
        
        # Include existing project context if available
        context_section = ""
        if project_context:
            context_section = f"""
EXISTING PROJECT FILES (be aware of what's already built):
{project_context[:1500]}

IMPORTANT: Do NOT recreate files that already exist. Instead, create NEW components that integrate with the existing codebase.
"""
        
        # Build comprehensive prompt
        prompt = f"""You are building a COMPLETE, PRODUCTION-READY frontend component.

TASK: {task}
{context_section}
CRITICAL REQUIREMENTS:
1. Output COMPLETE code - no placeholders, no "..." or "// add more here"
2. Start your code block with the FILENAME comment, like: // src/components/HeroSection.jsx
3. Include ALL imports at the top
4. Include FULL implementation with at least 100+ lines
5. Use modern React with hooks (useState, useEffect)
6. Include inline styles or styled-components for all styling
7. Add loading states, error handling, proper types
8. Mobile-responsive with CSS media queries
9. Dark theme by default with gradient accents (#667eea, #764ba2)

SUGGESTED FILE: {file_hint}

Output the COMPLETE component code in a single code block.
Start with: // src/components/YourComponentName.jsx"""

        result = self._call_llm(prompt)
        
        # If it's CSS-focused, also generate CSS
        if "css" in task_lower or "style" in task_lower:
            css_prompt = f"""Generate COMPLETE CSS for: {task}

Include:
- CSS variables for colors/spacing
- Dark mode as default
- Responsive breakpoints (mobile, tablet, desktop)
- Smooth transitions and hover effects
- At least 100+ lines of comprehensive CSS

Start with: /* src/styles/main.css */"""
            css_result = self._call_llm(css_prompt)
            result = result + "\n\n" + css_result
        
        return result


# Singleton
frontend_dev = FrontendDeveloper()
