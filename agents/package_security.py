"""
Package Security Verifier for Jarvis
Protects against malicious packages, typosquatting, and dependency confusion attacks.
"""
import os
import json
import re
from typing import Dict, List, Tuple
from difflib import SequenceMatcher

# === KNOWN MALICIOUS PACKAGES ===
# These are NEVER allowed - known malware/typosquats

NPM_BLACKLIST = {
    # Typosquats of popular packages
    "huggingface-cli",  # Fake - real is @huggingface/cli or huggingface-hub
    "crossenv",         # Malware - typosquat of cross-env
    "cross-env.js",     # Malware
    "d3.js",            # Malware - typosquat of d3
    "fabric-js",        # Malware - typosquat of fabric
    "ffmepg",           # Malware - typosquat of ffmpeg
    "gruntcli",         # Malware - typosquat of grunt-cli
    "http-proxy.js",    # Malware
    "jquery.js",        # Malware - typosquat of jquery
    "mariadb",          # Malware - use mysql2 or mariadb-connector
    "mongose",          # Malware - typosquat of mongoose
    "mssql.js",         # Malware
    "mssql-node",       # Malware
    "mysqljs",          # Malware - typosquat of mysql
    "node-hierarchical-data", # Malware
    "node-pre-gyp",     # Deprecated/compromised - use @mapbox/node-pre-gyp
    "node-fabric",      # Malware
    "nodecaffe",        # Malware
    "nodeffmpeg",       # Malware  
    "nodemailer-js",    # Malware - typosquat of nodemailer
    "nodesass",         # Malware - typosquat of node-sass
    "nodefabric",       # Malware
    "opencv.js",        # Malware
    "openssl.js",       # Malware
    "proxy.js",         # Malware
    "shadowsock",       # Malware - typosquat of shadowsocks
    "smb",              # Malware
    "sqlite.js",        # Malware
    "sqliter",          # Malware - typosquat of sqlite3
    "sqlserver",        # Malware
    "tkinter",          # Malware (npm doesn't have tkinter)
    "uglifyjs",         # Malware - typosquat of uglify-js
    "ws.js",            # Malware - typosquat of ws
    # Data exfiltration packages
    "discord-fix",
    "discord-lofy",
    "discord-selfbot",
    "discordsystem",
    "waaborern",
    "cxsodium",
    # Crypto miners
    "colourama",        # Typosquat of colorama
    "pptest",
    "urllib3proxy",
}

PIP_BLACKLIST = {
    # Known malware packages
    "huggingface-cli",  # Malware - real is huggingface-hub
    "python-binance",   # Use python-binance from PyPI carefully
    "beautifulsoup",    # Typosquat - real is beautifulsoup4
    "dateutil",         # Typosquat - real is python-dateutil
    "djago",            # Typosquat of django
    "djanga",           # Typosquat
    "fask",             # Typosquat of flask
    "falsk",            # Typosquat
    "httplib",          # Malware - use urllib3 or requests
    "maratlib",         # Malware
    "mlosk",            # Malware
    "opencv",           # Use opencv-python or opencv-contrib-python
    "openvc",           # Typosquat
    "py-style",         # Malware
    "pycolorz",         # Typosquat of colorama
    "pycrpto",          # Typosquat of pycrypto (use pycryptodome)
    "pycryptoo",        # Typosquat
    "pyexcel-ods3",     # Suspicious
    "pygrata",          # Malware
    "pyhton",           # Typosquat
    "pyinstaller2",     # Malware
    "pypi-download",    # Malware
    "python3-dateutil", # Typosquat
    "python-mongo",     # Use pymongo
    "reqeusts",         # Typosquat of requests
    "request",          # Typosquat of requests
    "requestss",        # Typosquat
    "requestes",        # Typosquat
    "sklearn",          # Use scikit-learn
    "sklearnm",         # Typosquat
    "sqlachemy",        # Typosquat of sqlalchemy
    "sqlalchmey",       # Typosquat
    "tenserflow",       # Typosquat of tensorflow
    "tensorflwo",       # Typosquat
    "torch-nightly",    # Suspicious - use pytorch nightly from official
    "torchcv",          # Suspicious
    "urllib",           # Malware - use urllib3
    "virtualenv2",      # Malware
}

# === LEGITIMATE PACKAGE MAPPINGS ===
# Common mistakes -> correct package

CORRECT_PACKAGES = {
    # npm
    "huggingface-cli": "@huggingface/cli or huggingface",
    "cross-env.js": "cross-env",
    "fabric-js": "fabric",
    "jquery.js": "jquery",
    "node-pre-gyp": "@mapbox/node-pre-gyp",
    "nodemailer-js": "nodemailer",
    "uglifyjs": "uglify-js",
    # pip
    "beautifulsoup": "beautifulsoup4",
    "dateutil": "python-dateutil",
    "opencv": "opencv-python",
    "sklearn": "scikit-learn",
    "request": "requests",
    "pycrypto": "pycryptodome",
}

# === TRUSTED PUBLISHERS/SCOPES ===
NPM_TRUSTED_SCOPES = {
    "@types",           # TypeScript types
    "@babel",
    "@emotion",
    "@mui",
    "@radix-ui",
    "@testing-library",
    "@tanstack",
    "@trpc",
    "@prisma",
    "@supabase",
    "@vercel",
    "@nestjs",
    "@angular",
    "@vue",
    "@nuxt",
    "@svelte",
    "@reduxjs",
    "@apollo",
    "@graphql",
    "@aws-sdk",
    "@google-cloud",
    "@azure",
    "@octokit",
    "@huggingface",
    "@mapbox",
}


class PackageSecurityVerifier:
    """
    Verifies package safety before installation.
    
    Checks:
    1. Known malware blacklist
    2. Typosquatting detection
    3. Package age/popularity (future)
    4. Dependency confusion detection
    """
    
    def __init__(self):
        self.npm_blacklist = NPM_BLACKLIST
        self.pip_blacklist = PIP_BLACKLIST
        self.trusted_scopes = NPM_TRUSTED_SCOPES
    
    def check_npm_package(self, package: str) -> Dict:
        """
        Check if npm package is safe to install.
        
        Returns:
            {
                "safe": bool,
                "risk": "none" | "low" | "medium" | "high" | "blocked",
                "reason": str,
                "suggestion": str | None
            }
        """
        package_lower = package.lower().strip()
        
        # Remove version specifier
        base_package = package_lower.split("@")[0] if not package_lower.startswith("@") else package_lower
        
        # Check trusted scopes first
        if package_lower.startswith("@"):
            scope = package_lower.split("/")[0]
            if scope in self.trusted_scopes:
                return {
                    "safe": True,
                    "risk": "none",
                    "reason": f"Trusted scope: {scope}",
                    "suggestion": None
                }
        
        # Check blacklist
        if base_package in self.npm_blacklist:
            suggestion = CORRECT_PACKAGES.get(base_package)
            return {
                "safe": False,
                "risk": "blocked",
                "reason": f"BLOCKED: '{base_package}' is a known malicious package",
                "suggestion": f"Did you mean: {suggestion}" if suggestion else "This package is malware. Do not install."
            }
        
        # Check for typosquatting of popular packages
        typosquat_check = self._check_typosquat(base_package, "npm")
        if typosquat_check:
            return {
                "safe": False,
                "risk": "high",
                "reason": f"Possible typosquat of '{typosquat_check}'",
                "suggestion": f"Did you mean: {typosquat_check}?"
            }
        
        # Check for suspicious patterns
        if self._has_suspicious_pattern(base_package):
            return {
                "safe": False,
                "risk": "medium",
                "reason": "Suspicious package name pattern",
                "suggestion": "Verify this package on npmjs.com before installing"
            }
        
        return {
            "safe": True,
            "risk": "low",
            "reason": "No known issues",
            "suggestion": None
        }
    
    def check_pip_package(self, package: str) -> Dict:
        """
        Check if pip package is safe to install.
        """
        package_lower = package.lower().strip()
        
        # Remove version specifier
        base_package = re.split(r'[<>=!~\[]', package_lower)[0]
        
        # Check blacklist
        if base_package in self.pip_blacklist:
            suggestion = CORRECT_PACKAGES.get(base_package)
            return {
                "safe": False,
                "risk": "blocked",
                "reason": f"BLOCKED: '{base_package}' is a known malicious package",
                "suggestion": f"Did you mean: {suggestion}" if suggestion else "This package is malware. Do not install."
            }
        
        # Check for typosquatting
        typosquat_check = self._check_typosquat(base_package, "pip")
        if typosquat_check:
            return {
                "safe": False,
                "risk": "high",
                "reason": f"Possible typosquat of '{typosquat_check}'",
                "suggestion": f"Did you mean: {typosquat_check}?"
            }
        
        # Check for suspicious patterns
        if self._has_suspicious_pattern(base_package):
            return {
                "safe": False,
                "risk": "medium",
                "reason": "Suspicious package name pattern",
                "suggestion": "Verify this package on pypi.org before installing"
            }
        
        return {
            "safe": True,
            "risk": "low",
            "reason": "No known issues",
            "suggestion": None
        }
    
    def verify_requirements_txt(self, file_path: str) -> List[Dict]:
        """
        Verify all packages in a requirements.txt file.
        """
        results = []
        
        if not os.path.exists(file_path):
            return [{"error": "File not found"}]
        
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-"):
                    result = self.check_pip_package(line)
                    result["package"] = line
                    results.append(result)
        
        return results
    
    def verify_package_json(self, file_path: str) -> List[Dict]:
        """
        Verify all packages in a package.json file.
        """
        results = []
        
        if not os.path.exists(file_path):
            return [{"error": "File not found"}]
        
        with open(file_path, "r") as f:
            data = json.load(f)
        
        all_deps = {}
        all_deps.update(data.get("dependencies", {}))
        all_deps.update(data.get("devDependencies", {}))
        
        for package in all_deps:
            result = self.check_npm_package(package)
            result["package"] = package
            results.append(result)
        
        return results
    
    def _check_typosquat(self, package: str, ecosystem: str) -> str | None:
        """
        Check if package name is similar to a popular package.
        Uses fuzzy matching.
        """
        popular_npm = [
            "react", "vue", "angular", "express", "lodash", "axios", "webpack",
            "typescript", "eslint", "prettier", "jest", "mocha", "babel",
            "next", "nuxt", "gatsby", "vite", "rollup", "parcel",
            "mongoose", "sequelize", "prisma", "typeorm",
            "socket.io", "graphql", "apollo", "redux", "mobx",
            "tailwindcss", "bootstrap", "material-ui", "antd",
            "nodemon", "pm2", "dotenv", "cors", "helmet",
            "jsonwebtoken", "bcrypt", "passport", "multer",
            "chalk", "commander", "yargs", "inquirer",
            "puppeteer", "playwright", "cypress", "selenium-webdriver",
        ]
        
        popular_pip = [
            "requests", "flask", "django", "fastapi", "numpy", "pandas",
            "tensorflow", "torch", "pytorch", "scikit-learn", "scipy",
            "matplotlib", "seaborn", "plotly", "pillow", "opencv-python",
            "sqlalchemy", "pymongo", "redis", "celery", "boto3",
            "beautifulsoup4", "selenium", "playwright", "httpx", "aiohttp",
            "pydantic", "pytest", "black", "ruff", "mypy", "pylint",
            "cryptography", "pycryptodome", "passlib", "python-jose",
            "gunicorn", "uvicorn", "starlette", "alembic",
            "python-dotenv", "click", "typer", "rich", "tqdm",
            "huggingface-hub", "transformers", "tokenizers", "datasets",
        ]
        
        popular = popular_npm if ecosystem == "npm" else popular_pip
        
        for legit in popular:
            # Skip if exact match
            if package == legit:
                return None
            
            # Check similarity
            similarity = SequenceMatcher(None, package, legit).ratio()
            
            # High similarity but not exact = typosquat
            if similarity > 0.85 and similarity < 1.0:
                return legit
            
            # Common typosquat patterns
            if package == legit.replace("-", ""):  # removed hyphen
                return legit
            if package == legit + "js" or package == legit + ".js":
                return legit
            if package == legit + "-js":
                return legit
            if package == "py" + legit or package == "python-" + legit:
                if legit not in ["python-dateutil", "python-dotenv", "python-jose"]:
                    return legit
        
        return None
    
    def _has_suspicious_pattern(self, package: str) -> bool:
        """
        Check for suspicious naming patterns.
        """
        suspicious = [
            r".*[-_]fix$",          # package-fix
            r".*[-_]patched$",      # package-patched
            r".*[-_]hacked$",       # obvious
            r".*[-_]discord.*",     # discord token stealers
            r".*[-_]token.*",       # token stealers
            r".*[-_]stealer.*",     # obvious
            r".*[-_]grabber.*",     # credential grabbers
            r".*miner.*",           # crypto miners
            r"^get[-_].*",          # get-package (common malware pattern)
            r".*[-_]free$",         # package-free
            r".*[-_]pro$",          # package-pro (fake premium)
            r".*[-_]crack.*",       # cracked software
            r".*[-_]keygen.*",      # keygens
        ]
        
        for pattern in suspicious:
            if re.match(pattern, package, re.IGNORECASE):
                return True
        
        return False


# Singleton
package_security = PackageSecurityVerifier()


def verify_install_command(command: str) -> Dict:
    """
    Verify a pip or npm install command before execution.
    
    Args:
        command: Full install command like "pip install requests flask"
        
    Returns:
        Dict with overall safety and per-package results
    """
    results = {
        "safe": True,
        "blocked": [],
        "warnings": [],
        "packages": []
    }
    
    # Parse command
    if "pip install" in command or "pip3 install" in command:
        ecosystem = "pip"
        # Extract package names
        parts = command.split()
        idx = parts.index("install") if "install" in parts else -1
        if idx >= 0:
            packages = [p for p in parts[idx+1:] if not p.startswith("-")]
    elif "npm install" in command or "npm i " in command:
        ecosystem = "npm"
        parts = command.split()
        idx = next((i for i, p in enumerate(parts) if p in ["install", "i"]), -1)
        if idx >= 0:
            packages = [p for p in parts[idx+1:] if not p.startswith("-")]
    else:
        return {"safe": True, "packages": [], "message": "Not an install command"}
    
    # Check each package
    for pkg in packages:
        if ecosystem == "pip":
            check = package_security.check_pip_package(pkg)
        else:
            check = package_security.check_npm_package(pkg)
        
        check["package"] = pkg
        results["packages"].append(check)
        
        if check["risk"] == "blocked":
            results["safe"] = False
            results["blocked"].append({
                "package": pkg,
                "reason": check["reason"],
                "suggestion": check.get("suggestion")
            })
        elif check["risk"] in ["high", "medium"]:
            results["warnings"].append({
                "package": pkg,
                "reason": check["reason"],
                "suggestion": check.get("suggestion")
            })
    
    return results
