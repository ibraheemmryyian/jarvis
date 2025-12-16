"""
Design Creativity Module for Jarvis v2
Injects unique design styles and layouts to prevent cookie-cutter outputs.
Forces the AI to think outside the typical "hero + 3 boxes" pattern.
"""
import random
from typing import Dict, List, Tuple


class DesignCreativity:
    """
    Generates unique design directions to inject into prompts.
    Breaks the AI out of typical template patterns.
    """
    
    # Unique layout patterns (NOT the typical hero + 3 boxes)
    LAYOUT_PATTERNS = [
        {
            "name": "Asymmetric Split",
            "description": "60/40 split layout with content on one side, visual on the other. Breaking grid intentionally.",
            "css_hints": "Use CSS Grid with asymmetric columns. One side bleeds off-screen."
        },
        {
            "name": "Scroll-Driven Story",
            "description": "Full-screen sections that tell a story as you scroll. Each section is a chapter.",
            "css_hints": "100vh sections, scroll-snap, parallax backgrounds"
        },
        {
            "name": "Bento Grid",
            "description": "Japanese bento-box inspired grid with varied cell sizes. Mix of content, images, stats.",
            "css_hints": "CSS Grid with grid-template-areas, irregular sizing like magazine layouts"
        },
        {
            "name": "Floating Cards",
            "description": "Cards that appear to float in 3D space at different depths and angles.",
            "css_hints": "transform: perspective(), rotateX/Y, translateZ for depth"
        },
        {
            "name": "Sidebar Navigation",
            "description": "Fixed sidebar with main content scrolling. Like a documentation site but for a product.",
            "css_hints": "position: sticky sidebar, scrollable main area"
        },
        {
            "name": "Horizontal Scroll",
            "description": "Sections scroll horizontally instead of vertically. Unique and memorable.",
            "css_hints": "overflow-x: scroll, display: flex with nowrap"
        },
        {
            "name": "Layered Depth",
            "description": "Multiple overlapping layers that create visual depth. Content peeks from behind.",
            "css_hints": "Absolute positioning, z-index layering, clip-path shapes"
        },
        {
            "name": "Full-Bleed Media",
            "description": "Giant full-screen images/videos with minimal text overlays. Visual-first.",
            "css_hints": "object-fit: cover, text over media with contrast backdrop"
        },
        {
            "name": "Brutalist",
            "description": "Bold, raw, unconventional. Oversized typography, harsh colors, intentionally jarring.",
            "css_hints": "Giant font sizes, system fonts, stark black/white with one accent"
        },
        {
            "name": "Organic Shapes",
            "description": "Blob shapes, curved sections, no straight lines. Feels human and approachable.",
            "css_hints": "border-radius: 50%, clip-path for blobs, SVG backgrounds"
        }
    ]
    
    # Color palette styles
    COLOR_STYLES = [
        {"name": "Neon Cyberpunk", "palette": ["#0f0f23", "#ff00ff", "#00ffff", "#ff6b6b", "#ffd93d"]},
        {"name": "Sunset Gradient", "palette": ["#1a1a2e", "#ff6b6b", "#feca57", "#48dbfb", "#ff9ff3"]},
        {"name": "Forest Calm", "palette": ["#0d1117", "#238636", "#58a6ff", "#c9d1d9", "#8b949e"]},
        {"name": "Monochrome Luxury", "palette": ["#000000", "#1a1a1a", "#333333", "#ffffff", "#gold"]},
        {"name": "Pastel Dreams", "palette": ["#fdf2f8", "#fce7f3", "#fbcfe8", "#f9a8d4", "#ec4899"]},
        {"name": "Ocean Depths", "palette": ["#0c1445", "#1e40af", "#3b82f6", "#60a5fa", "#93c5fd"]},
        {"name": "Warm Sand", "palette": ["#1c1917", "#78716c", "#d6d3d1", "#fef3c7", "#f59e0b"]},
        {"name": "Acid Green", "palette": ["#000000", "#84cc16", "#a3e635", "#ecfccb", "#65a30d"]},
    ]
    
    # Typography combinations
    TYPOGRAPHY = [
        {"heading": "Space Grotesk", "body": "Inter", "style": "Modern geometric"},
        {"heading": "Playfair Display", "body": "Source Sans Pro", "style": "Elegant serif"},
        {"heading": "Bebas Neue", "body": "Roboto", "style": "Bold impactful"},
        {"heading": "Clash Display", "body": "Satoshi", "style": "Contemporary"},
        {"heading": "Cabinet Grotesk", "body": "General Sans", "style": "Design agency"},
        {"heading": "Syne", "body": "Work Sans", "style": "Artistic"},
        {"heading": "Archivo Black", "body": "Archivo", "style": "Industrial"},
        {"heading": "Fraunces", "body": "Commissioner", "style": "Quirky editorial"},
    ]
    
    # Micro-interaction ideas
    MICRO_INTERACTIONS = [
        "Cursor follower - element that follows the mouse with spring physics",
        "Magnetic buttons - buttons that pull toward cursor when nearby",
        "Text reveal on scroll - letters animate in one by one",
        "Morphing shapes - SVG shapes that transform on hover",
        "Tilting cards - 3D tilt effect following mouse position",
        "Scramble text - letters scramble before resolving on hover",
        "Elastic scroll - content bounces at section boundaries",
        "Spotlight effect - radial gradient follows cursor",
        "Particle trail - particles follow mouse movement",
        "Liquid transitions - morphing blob transitions between sections",
    ]
    
    # Section alternatives (NOT the typical patterns)
    SECTION_ALTERNATIVES = {
        "hero": [
            "Split-screen video left, text right with typing animation",
            "Abstract 3D shape background with floating text",
            "Full-screen animated gradient with centered minimal text",
            "Newspaper-style layout with massive headline and columns",
            "Interactive canvas background that responds to mouse",
        ],
        "features": [
            "Timeline layout showing feature evolution",
            "Comparison table with competitors (we win)",
            "Interactive demo - click to see feature in action",
            "Before/after slider showing the transformation",
            "Orbiting icons around a central element",
        ],
        "pricing": [
            "Single featured plan with expandable details",
            "Slider to adjust usage, price updates live",
            "Comparison with 'DIY cost' vs 'our price'",
            "ROI calculator instead of static pricing",
            "Pay-what-you-want with suggested tiers",
        ],
        "testimonials": [
            "Video testimonials in a TikTok-style vertical scroll",
            "Twitter/X embed style cards",
            "Before/after case studies with metrics",
            "Rotating 3D carousel of company logos + quotes",
            "Masonry grid of varied testimonial sizes",
        ],
        "cta": [
            "Countdown timer creating urgency",
            "Interactive quiz leading to signup",
            "Email + instant preview of what they'll get",
            "Animated button that morphs on hover",
            "Chat widget that converts to signup",
        ],
    }
    
    def generate_design_direction(self) -> Dict:
        """
        Generate a unique design direction for a new project.
        Returns a complete creative brief to inject into prompts.
        """
        layout = random.choice(self.LAYOUT_PATTERNS)
        colors = random.choice(self.COLOR_STYLES)
        typography = random.choice(self.TYPOGRAPHY)
        interactions = random.sample(self.MICRO_INTERACTIONS, 3)
        
        return {
            "layout": layout,
            "colors": colors,
            "typography": typography,
            "interactions": interactions,
            "section_alternatives": {
                section: random.choice(alts)
                for section, alts in self.SECTION_ALTERNATIVES.items()
            }
        }
    
    def get_creative_prompt(self, base_objective: str) -> str:
        """
        Generate a creativity-enhanced prompt prefix.
        Injects unique design direction to break out of templates.
        """
        direction = self.generate_design_direction()
        
        prompt = f"""
## CRITICAL: UNIQUE DESIGN REQUIRED

You MUST create a website that is COMPLETELY DIFFERENT from typical templates.
DO NOT use the standard "hero section + 3 feature boxes + pricing cards" pattern.

### DESIGN DIRECTION (FOLLOW THIS):

**Layout Style**: {direction['layout']['name']}
- {direction['layout']['description']}
- CSS: {direction['layout']['css_hints']}

**Color Palette**: {direction['colors']['name']}
Colors: {', '.join(direction['colors']['palette'])}

**Typography**:
- Headings: {direction['typography']['heading']} ({direction['typography']['style']})
- Body: {direction['typography']['body']}
- Use Google Fonts: https://fonts.google.com

**Micro-Interactions** (implement at least 2):
"""
        for interaction in direction['interactions']:
            prompt += f"- {interaction}\n"
        
        prompt += "\n**Section Alternatives** (use THESE instead of typical patterns):\n"
        for section, alternative in direction['section_alternatives'].items():
            prompt += f"- {section.upper()}: {alternative}\n"
        
        prompt += f"""
### BANNED PATTERNS (DO NOT USE):
- Generic hero with centered text and gradient background
- 3 equal-width feature boxes in a row
- Standard 3-column pricing cards
- Circular avatar testimonial cards
- Basic sticky navbar with logo left, links right

### OBJECTIVE:
{base_objective}

Remember: Make this site MEMORABLE. Someone should screenshot it and share it because it's THAT good.
"""
        return prompt


# Singleton
design_creativity = DesignCreativity()
