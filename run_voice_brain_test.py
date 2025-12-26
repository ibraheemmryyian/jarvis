import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import autonomous_executor, recycler

OBJECTIVE = """
# PROJECT: VoiceBrain - The Voice-First Note Taker

## 1. Research & Analysis
- Research best browser-native Speech-to-Text APIs (Web Speech API vs others)
- Research local storage vs simple backend for saving notes
- **FLAW ANALYSIS (Phase 1.5)**: Critique your plan. Is client-side only better? Security?

## 2. Implementation
Create a Modern Web App (React + Vite) with:
- **UI**: Giant, pulsing "Record" button in center (Apple Voice Memos vibe).
- **Tech**: Use Web Speech API for real-time transcription.
- **Intelligence**: Mock an LLM call that categorizes text into [Task], [Idea], [Journal].
- **Display**: Masonry grid layout of notes cards.
- **Storage**: Use localStorage for MVP simplicity.

## 3. Deployment & Git
- **Phase 7**: Initialize git repo
- **Phase 8**: Create 'voice-brain' GitHub repo and push
- **Phase 9**: Deploy frontend to Netlify automatically

## OUTPUTS
- Working web app in `voice-brain` folder
- Live Netlify URL
- GitHub Repo URL
"""

def main():
    print("=" * 60)
    print("JARVIS A-to-Z AUTONOMY TEST: VoiceBrain")
    print("Testing: Research -> Flaw Analysis -> Code -> Git -> Deploy")
    print("=" * 60)
    
    # Run autonomous executor
    result = autonomous_executor.run(OBJECTIVE)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
    if result.get("status") == "complete":
        print(f"✅ Deployment: {result.get('deployment', {}).get('frontend', 'Not found')}")
        print(f"✅ GitHub: {result.get('github_url', 'Not found')}")
        print(f"📁 Path: {result.get('project_path')}")
    else:
        print(f"❌ Status: {result.get('status')}")
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    main()
