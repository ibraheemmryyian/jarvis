"""
Visual QA Agent for Jarvis v2
Uses Vision-Language Models to analyze screenshots and detect visual issues.
Works headlessly - no GUI required.
"""
import os
import base64
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
from .config import WORKSPACE_DIR

# LM Studio URL for vision model (Qwen-VL or similar)
VISION_MODEL_URL = "http://localhost:1234/v1/chat/completions"


class VisualQA:
    """
    Analyzes screenshots using Vision-Language Models.
    
    Detects:
    - Overlapping elements
    - Misaligned content
    - Missing images/broken assets
    - Color contrast issues
    - Layout corruption
    - Wrong/placeholder text
    - Mobile responsiveness issues
    """
    
    def __init__(self):
        self.results_dir = os.path.join(WORKSPACE_DIR, ".context", "visual_qa")
        os.makedirs(self.results_dir, exist_ok=True)
    
    def analyze_screenshot(self, image_path: str, page_context: str = "") -> Dict:
        """
        Analyze a screenshot for visual issues.
        
        Args:
            image_path: Path to screenshot file
            page_context: Optional context about what the page should look like
            
        Returns:
            Dict with analysis results and issues found
        """
        result = {
            "image": image_path,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "issues": [],
            "score": 0,  # 0-100 visual quality score
            "recommendations": []
        }
        
        if not os.path.exists(image_path):
            result["error"] = f"Image not found: {image_path}"
            return result
        
        # Encode image to base64
        try:
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            result["error"] = f"Failed to read image: {e}"
            return result
        
        # Determine image type
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif"
        }.get(ext, "image/png")
        
        # Build the vision prompt
        prompt = self._build_analysis_prompt(page_context)
        
        # Call vision model
        try:
            response = self._call_vision_model(image_data, mime_type, prompt)
            
            if response.get("error"):
                result["error"] = response["error"]
                return result
            
            # Parse the response
            analysis = self._parse_analysis(response.get("content", ""))
            result.update(analysis)
            result["success"] = True
            
        except Exception as e:
            result["error"] = f"Vision model error: {e}"
        
        return result
    
    def _build_analysis_prompt(self, context: str = "") -> str:
        """Build the prompt for visual analysis."""
        prompt = """Analyze this webpage screenshot for visual quality issues.

Check for the following problems and report each one you find:

1. **Overlapping Elements**: Text overlapping images, buttons overlapping other content
2. **Misalignment**: Elements not properly aligned, uneven spacing
3. **Broken Images**: Missing images, broken image icons, placeholder boxes
4. **Color Contrast**: Text hard to read against background
5. **Layout Corruption**: Elements in wrong positions, broken layout
6. **Placeholder Content**: Lorem ipsum text, "TODO" or placeholder text
7. **Cut-off Content**: Text or images cut off at edges
8. **Responsive Issues**: Content not fitting properly, horizontal scroll
9. **Font Issues**: Missing fonts, inconsistent typography
10. **Z-Index Problems**: Wrong stacking order, elements hidden behind others

For each issue found, provide:
- Issue type (from the list above)
- Location (top/middle/bottom, left/center/right)
- Severity (critical/major/minor)
- Description

Also provide:
- Overall visual quality score (0-100)
- Top 3 recommendations for improvement

Respond in this exact JSON format:
```json
{
  "issues": [
    {"type": "Overlapping Elements", "location": "top-right", "severity": "major", "description": "Navigation menu overlaps hero image"}
  ],
  "score": 85,
  "recommendations": [
    "Fix navigation z-index to prevent overlap",
    "Add more contrast to call-to-action button"
  ]
}
```

If no issues are found, return an empty issues array and score of 100.
"""
        
        if context:
            prompt += f"\n\nAdditional context about this page:\n{context}"
        
        return prompt
    
    def _call_vision_model(self, image_base64: str, mime_type: str, prompt: str) -> Dict:
        """Call the vision-language model."""
        
        # Format for LM Studio / OpenAI-compatible vision API
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "temperature": 0.2,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                VISION_MODEL_URL, 
                json=payload, 
                timeout=300  # 5 min timeout for vision analysis
            )
            
            if response.status_code != 200:
                return {"error": f"Vision API error: {response.status_code}"}
            
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {"content": content}
            
        except requests.exceptions.ConnectionError:
            return {"error": "Vision model not running. Load Qwen-VL or similar in LM Studio."}
        except requests.exceptions.Timeout:
            return {"error": "Vision model timeout. Image may be too large."}
        except Exception as e:
            return {"error": str(e)}
    
    def _parse_analysis(self, response: str) -> Dict:
        """Parse the vision model's response."""
        result = {
            "issues": [],
            "score": 0,
            "recommendations": []
        }
        
        # Try to extract JSON from response
        try:
            # Look for JSON block
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                # Try direct parse
                json_str = response
            
            data = json.loads(json_str.strip())
            result["issues"] = data.get("issues", [])
            result["score"] = data.get("score", 0)
            result["recommendations"] = data.get("recommendations", [])
            
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract info manually
            result["raw_response"] = response
            
            # Simple heuristics
            if "no issues" in response.lower() or "looks good" in response.lower():
                result["score"] = 90
            elif "critical" in response.lower():
                result["score"] = 30
            elif "major" in response.lower():
                result["score"] = 50
            else:
                result["score"] = 70
        
        return result
    
    def analyze_project(self, project_path: str) -> Dict:
        """
        Analyze all screenshots from a project's browser tests.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Dict with visual QA results for all pages
        """
        from .browser_tester import browser_tester
        
        results = {
            "project": project_path,
            "timestamp": datetime.now().isoformat(),
            "pages_analyzed": [],
            "total_issues": 0,
            "average_score": 0,
            "critical_issues": []
        }
        
        # First, run browser tests to get screenshots
        print("[Visual QA] Taking screenshots...")
        browser_results = browser_tester.test_project(project_path)
        
        scores = []
        
        # Analyze each screenshot
        for file_result in browser_results.get("files_tested", []):
            screenshot = file_result.get("screenshot")
            if screenshot and os.path.exists(screenshot):
                print(f"[Visual QA] Analyzing: {os.path.basename(screenshot)}")
                
                analysis = self.analyze_screenshot(
                    screenshot, 
                    f"Page: {file_result.get('file', 'unknown')}"
                )
                
                results["pages_analyzed"].append({
                    "page": file_result.get("file"),
                    "screenshot": screenshot,
                    "analysis": analysis
                })
                
                if analysis.get("success"):
                    scores.append(analysis.get("score", 0))
                    results["total_issues"] += len(analysis.get("issues", []))
                    
                    # Track critical issues
                    for issue in analysis.get("issues", []):
                        if issue.get("severity") == "critical":
                            results["critical_issues"].append({
                                "page": file_result.get("file"),
                                "issue": issue
                            })
            
            # Also check mobile screenshot
            for viewport_test in file_result.get("viewport_tests", []):
                mobile_screenshot = viewport_test.get("screenshot")
                if mobile_screenshot and os.path.exists(mobile_screenshot):
                    print(f"[Visual QA] Analyzing mobile: {os.path.basename(mobile_screenshot)}")
                    
                    analysis = self.analyze_screenshot(
                        mobile_screenshot,
                        f"Mobile view of: {file_result.get('file', 'unknown')}"
                    )
                    
                    results["pages_analyzed"].append({
                        "page": f"{file_result.get('file')} (mobile)",
                        "screenshot": mobile_screenshot,
                        "analysis": analysis
                    })
                    
                    if analysis.get("success"):
                        scores.append(analysis.get("score", 0))
                        results["total_issues"] += len(analysis.get("issues", []))
        
        # Calculate average score
        if scores:
            results["average_score"] = round(sum(scores) / len(scores), 1)
        
        # Determine overall pass/fail
        results["passed"] = results["average_score"] >= 70 and len(results["critical_issues"]) == 0
        
        # Save results
        self._save_results(project_path, results)
        
        return results
    
    def _save_results(self, project_path: str, results: Dict):
        """Save visual QA results to project."""
        jarvis_dir = os.path.join(project_path, ".jarvis")
        os.makedirs(jarvis_dir, exist_ok=True)
        
        results_path = os.path.join(jarvis_dir, "visual_qa.json")
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"[Visual QA] Results saved to {results_path}")
    
    def quick_check(self, image_path: str) -> str:
        """
        Quick visual check - returns a simple pass/fail summary.
        
        Args:
            image_path: Path to screenshot
            
        Returns:
            Human-readable summary string
        """
        result = self.analyze_screenshot(image_path)
        
        if not result.get("success"):
            return f"❌ Visual QA failed: {result.get('error', 'Unknown error')}"
        
        score = result.get("score", 0)
        issues = result.get("issues", [])
        
        if score >= 90 and len(issues) == 0:
            return f"✅ Visual QA passed! Score: {score}/100"
        elif score >= 70:
            return f"⚠️ Visual QA passed with warnings. Score: {score}/100. {len(issues)} issues found."
        else:
            critical = len([i for i in issues if i.get("severity") == "critical"])
            return f"❌ Visual QA failed. Score: {score}/100. {len(issues)} issues ({critical} critical)."


# Singleton instance
visual_qa = VisualQA()
