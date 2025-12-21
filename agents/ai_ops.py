"""
AI/ML Ops Agent for Jarvis
Specializes in ML pipelines, model deployment, AI infrastructure.
"""
from .base_agent import BaseAgent


class AIBackendOps(BaseAgent):
    """Expert in AI/ML operations, model serving, and pipelines."""
    
    def __init__(self):
        super().__init__("ai_ops")
    
    def _get_system_prompt(self) -> str:
        return """You are an Expert AI/ML Operations Engineer.

SPECIALTIES:
- LLM integration (OpenAI, Anthropic, local models)
- Model serving (vLLM, TGI, Triton)
- Vector databases (Pinecone, Qdrant, Chroma)
- RAG pipelines (LangChain, LlamaIndex)
- Fine-tuning pipelines
- Prompt engineering and optimization

INFRASTRUCTURE:
- Python ML stack (transformers, torch, sklearn)
- GPU orchestration (CUDA, Docker)
- Model versioning and tracking
- Feature stores
- A/B testing for models
- Observability (latency, costs, quality)

BEST PRACTICES:
- Async/streaming responses
- Token usage optimization
- Caching strategies
- Fallback handling
- Rate limiting
- Cost management

OUTPUT FORMAT:
For AI integrations, output:
1. Complete Python code
2. Config files
3. Docker setup if needed
4. Environment variables list
5. Testing strategy"""
    
    def create_llm_integration(self, description: str) -> str:
        """Create an LLM integration with proper handling."""
        prompt = f"""Create a production-ready LLM integration:

{description}

Include:
- Client setup with retries
- Streaming support
- Token counting
- Cost tracking
- Error handling with fallbacks
- Caching layer

Output complete code."""
        return self._call_llm(prompt)
    
    def create_rag_pipeline(self, description: str) -> str:
        """Create a RAG pipeline with vector store."""
        prompt = f"""Create a RAG pipeline:

{description}

Include:
- Document loading and chunking
- Embedding generation
- Vector store setup
- Retrieval with reranking
- Context assembly
- Response generation

Output complete pipeline code."""
        return self._call_llm(prompt)
    
    def optimize_prompts(self, prompt: str) -> str:
        """Optimize a prompt for better results."""
        optimization_prompt = f"""Optimize this prompt for better LLM results:

ORIGINAL:
{prompt}

Improve:
- Clarity and structure
- Few-shot examples if helpful
- Output format specification
- Edge case handling

Output the optimized prompt with explanation."""
        return self._call_llm(optimization_prompt)
    
    def run(self, task: str) -> str:
        """Execute AI ops task."""
        task_lower = task.lower()
        if "rag" in task_lower or "retrieval" in task_lower:
            return self.create_rag_pipeline(task)
        elif "llm" in task_lower or "model" in task_lower:
            return self.create_llm_integration(task)
        elif "prompt" in task_lower and "optim" in task_lower:
            return self.optimize_prompts(task)
        else:
            return self._call_llm(f"AI/ML task: {task}")


# Singleton
ai_ops = AIBackendOps()
