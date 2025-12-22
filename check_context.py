"""Quick test to check context bloat"""
import sys
sys.path.insert(0, ".")

from agents.recycler import recycler
from agents.context_manager import context

# Check context stats
print("=== CONTEXT STATS ===")
stats = recycler.get_context_stats()
total = sum(s['size_tokens'] for s in stats.values())
print(f"Total tokens in context files: {total}")
for k, v in stats.items():
    if v['size_tokens'] > 0:
        print(f"  {k}: {v['size_tokens']} tokens")

# Check what autonomous agent would receive
print("\n=== AUTONOMOUS AGENT CONTEXT ===")
ctx = context.read_for_agent("autonomous")
print(f"Context length: {len(ctx)} chars (~{len(ctx)//4} tokens)")
