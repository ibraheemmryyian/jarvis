"""Test what the planner is returning"""
from agents.autonomous import AutonomousExecutor

ex = AutonomousExecutor()

prompt = """Break down this objective into concrete steps:

OBJECTIVE: Build a web app that lets me upload a 14-page PDF waste valorization report and generates a professional cold outreach email for C-suite contacts and SME businesses. Dark theme, modern UI.

RULES:
- Each step should produce something COMPLETE and WORKING
- Don't split "Create component" and "Add styling" - combine them
- Quality over quantity

Output a numbered list of 5-10 specific steps.
Format: Just the numbered list."""

print("Calling LLM...")
response = ex._call_llm(prompt)
print(f"\n=== RESPONSE LENGTH: {len(response)} chars ===")
print("\n=== FULL RESPONSE ===")
print(response)
