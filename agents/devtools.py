"""
DevTools Agent for Jarvis v2
CTO-level development tools: linting, formatting, testing, analysis, Docker, database.
"""
import os
import subprocess
import json
from typing import Dict, List, Optional, Tuple
from .base_agent import BaseAgent
from .config import WORKSPACE_DIR


class DevTools:
    """
    CTO-level development tools for production-quality code.
    
    Features:
    - Code linting (ESLint, Pylint, Ruff)
    - Code formatting (Prettier, Black, Ruff format)
    - Test running with coverage
    - Dependency auditing (npm audit, pip-audit)
    - Docker management
    - Database migrations
    - API testing
    - Code metrics
    """
    
    def __init__(self):
        self.timeout = 120  # 2 minutes max per operation
    
    def _run(self, cmd: List[str], cwd: str = None, timeout: int = None) -> Dict:
        """Run a command and return structured result."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or WORKSPACE_DIR,
                capture_output=True,
                text=True,
                timeout=timeout or self.timeout,
                shell=True if os.name == 'nt' else False
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # === CODE LINTING ===
    
    def lint_python(self, project_path: str) -> Dict:
        """
        Lint Python code using Ruff (fast) or Pylint.
        Returns structured list of issues.
        """
        full_path = os.path.join(WORKSPACE_DIR, project_path) if not os.path.isabs(project_path) else project_path
        
        # Try Ruff first (faster)
        result = self._run(["python", "-m", "ruff", "check", full_path, "--output-format=json"])
        
        if result.get("success") or "ruff" not in result.get("error", ""):
            try:
                issues = json.loads(result.get("stdout", "[]"))
                return {
                    "tool": "ruff",
                    "success": True,
                    "issues": issues,
                    "count": len(issues)
                }
            except:
                pass
        
        # Fallback to pylint
        result = self._run(["python", "-m", "pylint", full_path, "--output-format=json"])
        try:
            issues = json.loads(result.get("stdout", "[]"))
            return {
                "tool": "pylint",
                "success": True,
                "issues": issues,
                "count": len(issues)
            }
        except:
            return {"success": False, "error": "No Python linter available"}
    
    def lint_javascript(self, project_path: str) -> Dict:
        """
        Lint JavaScript/TypeScript using ESLint.
        """
        full_path = os.path.join(WORKSPACE_DIR, project_path) if not os.path.isabs(project_path) else project_path
        
        # Check for ESLint config
        eslint_config = os.path.exists(os.path.join(full_path, ".eslintrc.json")) or \
                        os.path.exists(os.path.join(full_path, ".eslintrc.js")) or \
                        os.path.exists(os.path.join(full_path, "eslint.config.js"))
        
        if not eslint_config:
            # Create basic eslint config
            config = {
                "env": {"browser": True, "es2021": True, "node": True},
                "extends": ["eslint:recommended"],
                "parserOptions": {"ecmaVersion": "latest", "sourceType": "module"},
                "rules": {}
            }
            with open(os.path.join(full_path, ".eslintrc.json"), "w") as f:
                json.dump(config, f, indent=2)
        
        result = self._run(["npx", "eslint", ".", "--format=json"], cwd=full_path)
        
        try:
            issues = json.loads(result.get("stdout", "[]"))
            total_issues = sum(len(f.get("messages", [])) for f in issues)
            return {
                "tool": "eslint",
                "success": result.get("exit_code", 1) <= 1,  # 0 = no issues, 1 = has fixable issues
                "files_with_issues": len([f for f in issues if f.get("messages")]),
                "total_issues": total_issues,
                "issues": issues
            }
        except:
            return {"success": False, "error": result.get("stderr", "ESLint failed")}
    
    # === CODE FORMATTING ===
    
    def format_python(self, project_path: str, check_only: bool = False) -> Dict:
        """
        Format Python code using Black and isort.
        """
        full_path = os.path.join(WORKSPACE_DIR, project_path) if not os.path.isabs(project_path) else project_path
        
        results = {}
        
        # Black for code formatting
        args = ["python", "-m", "black", full_path]
        if check_only:
            args.append("--check")
        
        black_result = self._run(args)
        results["black"] = {
            "success": black_result.get("success", False),
            "output": black_result.get("stdout", "") + black_result.get("stderr", "")
        }
        
        # isort for import sorting
        args = ["python", "-m", "isort", full_path]
        if check_only:
            args.append("--check-only")
        
        isort_result = self._run(args)
        results["isort"] = {
            "success": isort_result.get("success", False),
            "output": isort_result.get("stdout", "") + isort_result.get("stderr", "")
        }
        
        return {
            "success": results["black"]["success"] and results["isort"]["success"],
            "results": results
        }
    
    def format_javascript(self, project_path: str, check_only: bool = False) -> Dict:
        """
        Format JavaScript/TypeScript using Prettier.
        """
        full_path = os.path.join(WORKSPACE_DIR, project_path) if not os.path.isabs(project_path) else project_path
        
        args = ["npx", "prettier"]
        if check_only:
            args.append("--check")
        else:
            args.append("--write")
        args.append(".")
        
        result = self._run(args, cwd=full_path)
        
        return {
            "tool": "prettier",
            "success": result.get("success", False),
            "output": result.get("stdout", "") + result.get("stderr", "")
        }
    
    # === TESTING ===
    
    def run_tests(self, project_path: str, coverage: bool = True) -> Dict:
        """
        Run tests with coverage.
        Auto-detects pytest, jest, or vitest.
        """
        full_path = os.path.join(WORKSPACE_DIR, project_path) if not os.path.isabs(project_path) else project_path
        
        # Detect test framework
        has_pytest = os.path.exists(os.path.join(full_path, "pytest.ini")) or \
                     os.path.exists(os.path.join(full_path, "pyproject.toml"))
        has_jest = "jest" in open(os.path.join(full_path, "package.json")).read() \
                   if os.path.exists(os.path.join(full_path, "package.json")) else False
        
        if has_pytest or any(f.startswith("test_") for f in os.listdir(full_path)):
            # Python tests
            args = ["python", "-m", "pytest", "-v"]
            if coverage:
                args.extend(["--cov=.", "--cov-report=json"])
            
            result = self._run(args, cwd=full_path)
            
            # Parse coverage if available
            cov_data = {}
            cov_file = os.path.join(full_path, "coverage.json")
            if os.path.exists(cov_file):
                with open(cov_file) as f:
                    cov_data = json.load(f)
            
            return {
                "framework": "pytest",
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "coverage": cov_data.get("totals", {}).get("percent_covered", 0) if cov_data else None
            }
        
        elif has_jest:
            # JavaScript tests
            args = ["npm", "test", "--", "--json"]
            if coverage:
                args.append("--coverage")
            
            result = self._run(args, cwd=full_path)
            
            return {
                "framework": "jest",
                "success": result.get("success", False),
                "output": result.get("stdout", "")
            }
        
        return {"success": False, "error": "No test framework detected"}
    
    # === DEPENDENCY MANAGEMENT ===
    
    def audit_dependencies(self, project_path: str) -> Dict:
        """
        Audit dependencies for security vulnerabilities.
        """
        full_path = os.path.join(WORKSPACE_DIR, project_path) if not os.path.isabs(project_path) else project_path
        
        results = {}
        
        # npm audit for JS
        if os.path.exists(os.path.join(full_path, "package.json")):
            result = self._run(["npm", "audit", "--json"], cwd=full_path)
            try:
                audit_data = json.loads(result.get("stdout", "{}"))
                results["npm"] = {
                    "vulnerabilities": audit_data.get("metadata", {}).get("vulnerabilities", {}),
                    "total": sum(audit_data.get("metadata", {}).get("vulnerabilities", {}).values())
                }
            except:
                results["npm"] = {"error": "Failed to parse npm audit"}
        
        # pip-audit for Python
        if os.path.exists(os.path.join(full_path, "requirements.txt")):
            result = self._run(["python", "-m", "pip_audit", "--format=json", "-r", 
                               os.path.join(full_path, "requirements.txt")])
            try:
                audit_data = json.loads(result.get("stdout", "[]"))
                results["pip"] = {
                    "vulnerabilities": audit_data,
                    "total": len(audit_data)
                }
            except:
                results["pip"] = {"error": "pip-audit not installed or failed"}
        
        return results
    
    def install_dependencies(self, project_path: str) -> Dict:
        """
        Install all project dependencies.
        """
        full_path = os.path.join(WORKSPACE_DIR, project_path) if not os.path.isabs(project_path) else project_path
        
        results = {}
        
        # npm install
        if os.path.exists(os.path.join(full_path, "package.json")):
            result = self._run(["npm", "install"], cwd=full_path)
            results["npm"] = {
                "success": result.get("success", False),
                "output": result.get("stderr", "")[:500]  # Truncate
            }
        
        # pip install
        req_file = os.path.join(full_path, "requirements.txt")
        if os.path.exists(req_file):
            result = self._run(["python", "-m", "pip", "install", "-r", req_file])
            results["pip"] = {
                "success": result.get("success", False),
                "output": result.get("stdout", "")[:500]
            }
        
        return results
    
    # === DOCKER ===
    
    def docker_build(self, project_path: str, tag: str = "latest") -> Dict:
        """
        Build Docker image for project.
        """
        full_path = os.path.join(WORKSPACE_DIR, project_path) if not os.path.isabs(project_path) else project_path
        project_name = os.path.basename(full_path).lower().replace(" ", "-")
        
        if not os.path.exists(os.path.join(full_path, "Dockerfile")):
            return {"success": False, "error": "No Dockerfile found"}
        
        result = self._run(["docker", "build", "-t", f"{project_name}:{tag}", "."], cwd=full_path)
        
        return {
            "success": result.get("success", False),
            "image": f"{project_name}:{tag}" if result.get("success") else None,
            "output": result.get("stdout", "") + result.get("stderr", "")
        }
    
    def docker_run(self, image: str, port: str = "3000:3000") -> Dict:
        """
        Run Docker container.
        """
        result = self._run(["docker", "run", "-d", "-p", port, image])
        
        container_id = result.get("stdout", "").strip()[:12] if result.get("success") else None
        
        return {
            "success": result.get("success", False),
            "container_id": container_id,
            "port": port.split(":")[0]
        }
    
    def create_dockerfile(self, project_path: str, project_type: str = "auto") -> Dict:
        """
        Generate a Dockerfile for the project.
        """
        full_path = os.path.join(WORKSPACE_DIR, project_path) if not os.path.isabs(project_path) else project_path
        
        # Auto-detect project type
        if project_type == "auto":
            if os.path.exists(os.path.join(full_path, "package.json")):
                project_type = "node"
            elif os.path.exists(os.path.join(full_path, "requirements.txt")):
                project_type = "python"
            else:
                project_type = "static"
        
        dockerfiles = {
            "node": """FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
""",
            "python": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
            "static": """FROM nginx:alpine
COPY . /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"""
        }
        
        dockerfile_content = dockerfiles.get(project_type, dockerfiles["static"])
        dockerfile_path = os.path.join(full_path, "Dockerfile")
        
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)
        
        return {
            "success": True,
            "type": project_type,
            "path": dockerfile_path
        }
    
    # === API TESTING ===
    
    def test_api(self, url: str, method: str = "GET", data: dict = None, headers: dict = None) -> Dict:
        """
        Test an API endpoint.
        """
        import urllib.request
        import urllib.error
        
        try:
            req = urllib.request.Request(url, method=method)
            
            if headers:
                for k, v in headers.items():
                    req.add_header(k, v)
            
            if data:
                req.data = json.dumps(data).encode()
                req.add_header("Content-Type", "application/json")
            
            with urllib.request.urlopen(req, timeout=30) as response:
                body = response.read().decode()
                try:
                    body = json.loads(body)
                except:
                    pass
                
                return {
                    "success": True,
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "body": body
                }
        
        except urllib.error.HTTPError as e:
            return {
                "success": False,
                "status_code": e.code,
                "error": str(e)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # === CODE METRICS ===
    
    def analyze_code(self, project_path: str) -> Dict:
        """
        Analyze code metrics: lines of code, complexity, etc.
        """
        full_path = os.path.join(WORKSPACE_DIR, project_path) if not os.path.isabs(project_path) else project_path
        
        metrics = {
            "files": {"py": 0, "js": 0, "jsx": 0, "ts": 0, "tsx": 0, "css": 0, "html": 0},
            "lines": {"code": 0, "blank": 0, "comment": 0},
            "functions": 0,
            "classes": 0
        }
        
        for root, dirs, files in os.walk(full_path):
            # Skip common noise
            dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', '.git', 'venv', 'dist']]
            
            for f in files:
                ext = f.split(".")[-1] if "." in f else ""
                if ext in metrics["files"]:
                    metrics["files"][ext] += 1
                    
                    try:
                        with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as file:
                            content = file.read()
                            lines = content.split("\n")
                            
                            for line in lines:
                                stripped = line.strip()
                                if not stripped:
                                    metrics["lines"]["blank"] += 1
                                elif stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("/*"):
                                    metrics["lines"]["comment"] += 1
                                else:
                                    metrics["lines"]["code"] += 1
                            
                            # Count functions/classes
                            if ext == "py":
                                metrics["functions"] += content.count("def ")
                                metrics["classes"] += content.count("class ")
                            elif ext in ["js", "jsx", "ts", "tsx"]:
                                metrics["functions"] += content.count("function ") + content.count("=> ")
                                metrics["classes"] += content.count("class ")
                    except:
                        pass
        
        return metrics
    
    # === DATABASE ===
    
    def run_migrations(self, project_path: str, db_type: str = "auto") -> Dict:
        """
        Run database migrations.
        Supports Alembic (Python/SQLAlchemy) and Prisma (Node).
        """
        full_path = os.path.join(WORKSPACE_DIR, project_path) if not os.path.isabs(project_path) else project_path
        
        # Detect migration tool
        if os.path.exists(os.path.join(full_path, "alembic.ini")) or db_type == "alembic":
            result = self._run(["python", "-m", "alembic", "upgrade", "head"], cwd=full_path)
            return {
                "tool": "alembic",
                "success": result.get("success", False),
                "output": result.get("stdout", "") + result.get("stderr", "")
            }
        
        elif os.path.exists(os.path.join(full_path, "prisma")) or db_type == "prisma":
            result = self._run(["npx", "prisma", "migrate", "deploy"], cwd=full_path)
            return {
                "tool": "prisma",
                "success": result.get("success", False),
                "output": result.get("stdout", "") + result.get("stderr", "")
            }
        
        return {"success": False, "error": "No migration tool detected"}
    
    def generate_migration(self, project_path: str, name: str) -> Dict:
        """
        Generate a new database migration.
        """
        full_path = os.path.join(WORKSPACE_DIR, project_path) if not os.path.isabs(project_path) else project_path
        
        # Alembic
        if os.path.exists(os.path.join(full_path, "alembic.ini")):
            result = self._run(["python", "-m", "alembic", "revision", "--autogenerate", "-m", name], 
                              cwd=full_path)
            return {
                "tool": "alembic",
                "success": result.get("success", False),
                "output": result.get("stdout", "") + result.get("stderr", "")
            }
        
        # Prisma
        elif os.path.exists(os.path.join(full_path, "prisma")):
            result = self._run(["npx", "prisma", "migrate", "dev", "--name", name], cwd=full_path)
            return {
                "tool": "prisma",
                "success": result.get("success", False),
                "output": result.get("stdout", "") + result.get("stderr", "")
            }
        
        return {"success": False, "error": "No migration tool detected"}
    
    # === ENVIRONMENT MANAGEMENT ===
    
    def create_env_file(self, project_path: str, variables: Dict[str, str] = None) -> Dict:
        """
        Create a .env file with common defaults and custom variables.
        """
        full_path = os.path.join(WORKSPACE_DIR, project_path) if not os.path.isabs(project_path) else project_path
        
        # Default env variables
        env_content = """# Environment Variables
# DO NOT commit this file to git!

# Server
NODE_ENV=development
PORT=3000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
# DATABASE_URL=sqlite:///./app.db

# Auth
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRY=7d

# APIs (add your keys here)
# OPENAI_API_KEY=sk-...
# STRIPE_SECRET_KEY=sk_test_...

"""
        if variables:
            env_content += "# Custom Variables\n"
            for key, value in variables.items():
                env_content += f"{key}={value}\n"
        
        env_path = os.path.join(full_path, ".env")
        with open(env_path, "w") as f:
            f.write(env_content)
        
        # Also create .env.example
        example_content = env_content.replace("your-super-secret", "change-this")
        with open(os.path.join(full_path, ".env.example"), "w") as f:
            f.write(example_content)
        
        # Add to .gitignore
        gitignore_path = os.path.join(full_path, ".gitignore")
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "a") as f:
                f.write("\n.env\n.env.local\n")
        
        return {"success": True, "path": env_path}
    
    def setup_venv(self, project_path: str, python_version: str = "3.11") -> Dict:
        """
        Create a Python virtual environment.
        """
        full_path = os.path.join(WORKSPACE_DIR, project_path) if not os.path.isabs(project_path) else project_path
        
        venv_path = os.path.join(full_path, "venv")
        
        result = self._run(["python", "-m", "venv", venv_path])
        
        if result.get("success"):
            # Create activation note
            note = f"""Virtual environment created at: {venv_path}

To activate:
  Windows: .\\venv\\Scripts\\activate
  Unix:    source venv/bin/activate
"""
            return {"success": True, "path": venv_path, "note": note}
        
        return result
    
    # === CI/CD ===
    
    def generate_github_actions(self, project_path: str, project_type: str = "auto") -> Dict:
        """
        Generate GitHub Actions CI/CD workflow.
        """
        full_path = os.path.join(WORKSPACE_DIR, project_path) if not os.path.isabs(project_path) else project_path
        
        # Auto-detect project type
        if project_type == "auto":
            if os.path.exists(os.path.join(full_path, "package.json")):
                project_type = "node"
            elif os.path.exists(os.path.join(full_path, "requirements.txt")):
                project_type = "python"
            else:
                project_type = "node"
        
        workflows = {
            "node": """name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run linting
      run: npm run lint || true
    
    - name: Run tests
      run: npm test || true
    
    - name: Build
      run: npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v25
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
        vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
        vercel-args: '--prod'
""",
            "python": """name: CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest ruff black
    
    - name: Lint with ruff
      run: ruff check . || true
    
    - name: Check formatting
      run: black --check . || true
    
    - name: Run tests
      run: pytest -v || true

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to Railway
      run: echo "Add your deployment steps here"
"""
        }
        
        # Create .github/workflows directory
        workflow_dir = os.path.join(full_path, ".github", "workflows")
        os.makedirs(workflow_dir, exist_ok=True)
        
        workflow_path = os.path.join(workflow_dir, "ci-cd.yml")
        with open(workflow_path, "w") as f:
            f.write(workflows.get(project_type, workflows["node"]))
        
        return {
            "success": True,
            "path": workflow_path,
            "type": project_type
        }
    
    # === DOCUMENTATION ===
    
    def generate_readme(self, project_path: str, project_name: str = None) -> Dict:
        """
        Generate a README.md based on project structure.
        """
        full_path = os.path.join(WORKSPACE_DIR, project_path) if not os.path.isabs(project_path) else project_path
        
        project_name = project_name or os.path.basename(full_path)
        
        # Detect project characteristics
        has_package_json = os.path.exists(os.path.join(full_path, "package.json"))
        has_requirements = os.path.exists(os.path.join(full_path, "requirements.txt"))
        has_docker = os.path.exists(os.path.join(full_path, "Dockerfile"))
        
        # Generate README
        readme = f"""# {project_name}

## Description

[Add project description here]

## Tech Stack

"""
        if has_package_json:
            readme += "- Node.js / JavaScript\n- npm\n"
        if has_requirements:
            readme += "- Python 3.11+\n- pip\n"
        if has_docker:
            readme += "- Docker\n"
        
        readme += """
## Getting Started

### Prerequisites

"""
        if has_package_json:
            readme += "- Node.js 18+ and npm\n"
        if has_requirements:
            readme += "- Python 3.11+\n"
        
        readme += """
### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/{project_name}.git
cd {project_name}

"""
        if has_package_json:
            readme += """# Install dependencies
npm install

# Run development server
npm run dev
```
"""
        elif has_requirements:
            readme += """# Create virtual environment
python -m venv venv
source venv/bin/activate  # or .\\venv\\Scripts\\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```
"""
        
        readme += """
## Environment Variables

Copy `.env.example` to `.env` and fill in your values.

## License

MIT
"""
        
        readme_path = os.path.join(full_path, "README.md")
        with open(readme_path, "w") as f:
            f.write(readme)
        
        return {"success": True, "path": readme_path}
    
    def generate_changelog(self, project_path: str) -> Dict:
        """
        Initialize a CHANGELOG.md following Keep a Changelog format.
        """
        full_path = os.path.join(WORKSPACE_DIR, project_path) if not os.path.isabs(project_path) else project_path
        
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        
        changelog = f"""# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup

## [0.1.0] - {today}

### Added
- Project initialized
- Core functionality implemented
- Documentation added

[Unreleased]: https://github.com/yourusername/project/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/project/releases/tag/v0.1.0
"""
        
        changelog_path = os.path.join(full_path, "CHANGELOG.md")
        with open(changelog_path, "w") as f:
            f.write(changelog)
        
        return {"success": True, "path": changelog_path}


# Singleton
devtools = DevTools()
