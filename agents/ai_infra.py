"""
AI Infrastructure Agent for Jarvis
Specializes in cloud infrastructure for AI workloads - GPU servers, model serving, scaling.
"""
from .base_agent import BaseAgent


class AIInfrastructure(BaseAgent):
    """Expert in AI/ML infrastructure, GPU orchestration, model deployment."""
    
    def __init__(self):
        super().__init__("ai_infra")
    
    def _get_system_prompt(self) -> str:
        return """You are a Senior AI Infrastructure Engineer.

SPECIALTIES:
- GPU server provisioning (NVIDIA, AMD)
- Model serving infrastructure (vLLM, TGI, Triton)
- Container orchestration for AI (Kubernetes, Docker)
- Cloud platforms (AWS Bedrock/SageMaker, GCP Vertex, Azure ML)
- Edge AI deployment
- Cost optimization for GPU workloads

INFRASTRUCTURE STACK:
- Docker + NVIDIA Container Toolkit
- Kubernetes + GPU operators
- Ray for distributed compute
- Terraform/Pulumi for IaC
- Model registries (MLflow, Weights & Biases)
- Monitoring (Prometheus, Grafana, custom metrics)

SCALING PATTERNS:
- Horizontal pod autoscaling with GPU metrics
- Queue-based batch processing
- Serverless inference (Lambda, Cloud Run)
- Multi-GPU / Multi-node training
- Model sharding for large models

OPTIMIZATION:
- GPU memory optimization
- Batching strategies
- Quantization deployment (INT8, FP16)
- KV cache optimization
- Speculative decoding setup

OUTPUT FORMAT:
For infrastructure, output:
1. Architecture diagram (mermaid)
2. Infrastructure code (Docker, K8s, Terraform)
3. Configuration files
4. Cost estimation
5. Scaling recommendations"""
    
    def create_docker_setup(self, model_type: str, gpu_requirements: str = "1x RTX 4090") -> str:
        """Create Docker setup for AI model serving."""
        prompt = f"""Create a production Docker setup for AI model serving:

MODEL TYPE: {model_type}
GPU: {gpu_requirements}

Include:
- Dockerfile with CUDA support
- docker-compose.yml with GPU passthrough
- Health check endpoint
- Volume mounts for models
- Environment configuration
- Resource limits

Output complete files."""
        return self._call_llm(prompt)
    
    def create_k8s_deployment(self, service_name: str, replicas: int = 2) -> str:
        """Create Kubernetes deployment for AI services."""
        prompt = f"""Create Kubernetes deployment for AI service:

SERVICE: {service_name}
REPLICAS: {replicas}

Include:
- Deployment with GPU resource requests
- Service and Ingress
- HPA with custom GPU metrics
- ConfigMap for model config
- PVC for model storage
- NVIDIA device plugin annotations

Output complete YAML manifests."""
        return self._call_llm(prompt)
    
    def create_terraform(self, cloud: str, spec: str) -> str:
        """Create Terraform for AI infrastructure."""
        prompt = f"""Create Terraform for AI infrastructure:

CLOUD: {cloud}
SPECIFICATION: {spec}

Include:
- GPU instance provisioning
- VPC/networking
- Load balancer
- Storage for models
- IAM/security
- Auto-scaling config

Output complete Terraform files."""
        return self._call_llm(prompt)
    
    def optimize_inference(self, model: str, current_latency: str = None) -> str:
        """Optimize inference infrastructure."""
        prompt = f"""Optimize AI inference infrastructure:

MODEL: {model}
CURRENT LATENCY: {current_latency or 'Unknown'}

Analyze and recommend:
- Quantization strategy
- Batching configuration
- Caching layer setup
- Model sharding (if needed)
- Hardware recommendations
- Expected improvements

Output actionable config changes."""
        return self._call_llm(prompt)
    
    def cost_analysis(self, workload: str) -> str:
        """Analyze and optimize AI infrastructure costs."""
        prompt = f"""AI infrastructure cost analysis:

WORKLOAD: {workload}

Include:
- Current cost estimation
- Spot/preemptible opportunities
- Reserved capacity recommendations
- Scaling inefficiencies
- Alternative architectures
- Monthly cost projection

Compare AWS vs GCP vs Azure options."""
        return self._call_llm(prompt)
    
    def run(self, task: str) -> str:
        """Execute AI infrastructure task."""
        task_lower = task.lower()
        if "docker" in task_lower:
            return self.create_docker_setup(task)
        elif "kubernetes" in task_lower or "k8s" in task_lower:
            return self.create_k8s_deployment(task)
        elif "terraform" in task_lower or "cloud" in task_lower:
            return self.create_terraform("aws", task)
        elif "optim" in task_lower or "latency" in task_lower:
            return self.optimize_inference(task)
        elif "cost" in task_lower:
            return self.cost_analysis(task)
        else:
            return self._call_llm(f"AI infrastructure task: {task}")


# Singleton
ai_infra = AIInfrastructure()
