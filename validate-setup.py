#!/usr/bin/env python3
"""
FortiGate Project Setup Validation Script
Validates all initialization components and configurations
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SetupValidator:
    """Comprehensive setup validation for FortiGate project"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.errors = []
        self.warnings = []
        self.checks_passed = 0
        self.total_checks = 0
    
    def run_validation(self) -> bool:
        """Run comprehensive validation suite"""
        logger.info("🔍 Starting FortiGate project validation...")
        
        validations = [
            ("Environment Files", self._validate_environment_files),
            ("Configuration Files", self._validate_config_files),
            ("Project Structure", self._validate_project_structure),
            ("Dependencies", self._validate_dependencies),
            ("Python Syntax", self._validate_python_syntax),
            ("Import Validation", self._validate_imports),
            ("Service Configuration", self._validate_service_config),
            ("Security Settings", self._validate_security_settings)
        ]
        
        for name, validation_func in validations:
            logger.info(f"📋 Validating: {name}")
            try:
                validation_func()
                logger.info(f"✅ {name}: PASSED")
            except Exception as e:
                self.errors.append(f"{name}: {e}")
                logger.error(f"❌ {name}: FAILED - {e}")
        
        return self._generate_report()
    
    def _check(self, description: str, condition: bool, warning: str = None):
        """Helper to track validation checks"""
        self.total_checks += 1
        if condition:
            self.checks_passed += 1
        else:
            if warning:
                self.warnings.append(f"{description}: {warning}")
            else:
                self.errors.append(description)
    
    def _validate_environment_files(self):
        """Validate environment configuration files"""
        required_env_files = [".env.dev", ".env.prod", ".env.k8s"]
        
        for env_file in required_env_files:
            file_path = self.project_root / env_file
            self._check(f"Environment file {env_file} exists", file_path.exists())
            
            if file_path.exists():
                content = file_path.read_text()
                
                # Check for required sections
                required_sections = [
                    "# Application Settings",
                    "APP_MODE=",
                    "WEB_APP_PORT=",
                    "# Security Configuration"
                ]
                
                for section in required_sections:
                    self._check(
                        f"{env_file} contains {section}",
                        section in content
                    )
    
    def _validate_config_files(self):
        """Validate configuration files"""
        config_files = {
            "mcp-tools-config.json": ["version", "mcp_servers", "native_agents"],
            "agent-config.json": ["version", "agents", "workflows"],
            "initialization-report.json": ["timestamp", "status", "components"]
        }
        
        for config_file, required_keys in config_files.items():
            file_path = self.project_root / config_file
            self._check(f"Config file {config_file} exists", file_path.exists())
            
            if file_path.exists():
                try:
                    with open(file_path) as f:
                        config_data = json.load(f)
                    
                    for key in required_keys:
                        self._check(
                            f"{config_file} contains key '{key}'",
                            key in config_data
                        )
                        
                except json.JSONDecodeError as e:
                    self.errors.append(f"{config_file} invalid JSON: {e}")
    
    def _validate_project_structure(self):
        """Validate project directory structure"""
        required_dirs = [
            "src", "tests", "config", "data", "logs", 
            "temp", "exports", "backup", "charts", "k8s"
        ]
        
        for directory in required_dirs:
            dir_path = self.project_root / directory
            self._check(f"Directory {directory} exists", dir_path.exists())
        
        # Check critical Python files
        critical_files = [
            "src/main.py",
            "src/web_app.py", 
            "requirements.txt",
            "pyproject.toml"
        ]
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            self._check(f"Critical file {file_path} exists", full_path.exists())
    
    def _validate_dependencies(self):
        """Validate Python dependencies"""
        requirements_file = self.project_root / "requirements.txt"
        self._check("requirements.txt exists", requirements_file.exists())
        
        if requirements_file.exists():
            with open(requirements_file) as f:
                requirements = f.read()
            
            # Check for critical dependencies
            critical_deps = [
                "flask", "redis", "requests", "jinja2", 
                "gunicorn", "pytest", "black", "flake8"
            ]
            
            for dep in critical_deps:
                self._check(
                    f"Dependency {dep} in requirements",
                    dep.lower() in requirements.lower(),
                    f"Consider adding {dep} to requirements.txt"
                )
    
    def _validate_python_syntax(self):
        """Validate Python syntax for main files"""
        python_files = [
            "src/main.py",
            "src/web_app.py",
            "init-project.py"
        ]
        
        for py_file in python_files:
            file_path = self.project_root / py_file
            if file_path.exists():
                try:
                    result = subprocess.run([
                        sys.executable, "-m", "py_compile", str(file_path)
                    ], capture_output=True, text=True, check=True)
                    self._check(f"Python syntax valid for {py_file}", True)
                except subprocess.CalledProcessError as e:
                    self.errors.append(f"Python syntax error in {py_file}: {e.stderr}")
    
    def _validate_imports(self):
        """Validate critical Python imports"""
        sys.path.insert(0, str(self.project_root / "src"))
        
        critical_imports = [
            ("main", "src/main.py"),
            ("web_app", "src/web_app.py"),
            ("utils.unified_logger", "logging module"),
        ]
        
        for module_name, description in critical_imports:
            try:
                __import__(module_name)
                self._check(f"Import {description} successful", True)
            except ImportError as e:
                self._check(
                    f"Import {description} failed", 
                    False,
                    f"Import error: {e}"
                )
    
    def _validate_service_config(self):
        """Validate service configurations"""
        # Check Flask app creation
        try:
            from web_app import create_app
            app = create_app()
            self._check("Flask app creation successful", app is not None)
        except Exception as e:
            self.errors.append(f"Flask app creation failed: {e}")
        
        # Check configuration loading
        try:
            from config.unified_settings import load_config
            config = load_config()
            self._check("Configuration loading successful", config is not None)
        except Exception as e:
            self._check(
                "Configuration loading failed",
                False,
                f"Config error: {e}"
            )
    
    def _validate_security_settings(self):
        """Validate security configurations"""
        env_dev_path = self.project_root / ".env.dev"
        
        if env_dev_path.exists():
            content = env_dev_path.read_text()
            
            # Check for secure defaults in development
            security_checks = [
                ("FLASK_DEBUG=true", "Debug mode enabled for development"),
                ("JWT_ACCESS_SECRET=", "JWT access secret configured"),
                ("JWT_REFRESH_SECRET=", "JWT refresh secret configured"),
                ("SECRET_KEY=", "Flask secret key configured")
            ]
            
            for check, description in security_checks:
                self._check(
                    f"Security setting: {description}",
                    check in content
                )
    
    def _generate_report(self) -> bool:
        """Generate validation report"""
        success_rate = (self.checks_passed / self.total_checks * 100) if self.total_checks > 0 else 0
        
        report = {
            "timestamp": "2025-08-14T03:45:00",
            "validation_summary": {
                "total_checks": self.total_checks,
                "checks_passed": self.checks_passed,
                "success_rate": f"{success_rate:.1f}%",
                "errors": len(self.errors),
                "warnings": len(self.warnings)
            },
            "status": "PASSED" if len(self.errors) == 0 else "FAILED",
            "errors": self.errors,
            "warnings": self.warnings,
            "recommendations": self._generate_recommendations()
        }
        
        # Save validation report
        with open("validation-report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("🔍 FortiGate Project Validation Report")
        print("="*60)
        print(f"✅ Checks Passed: {self.checks_passed}/{self.total_checks} ({success_rate:.1f}%)")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"📊 Overall Status: {report['status']}")
        
        if self.errors:
            print("\n❌ Critical Issues:")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if self.warnings:
            print("\n⚠️  Warnings:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        print(f"\n📄 Full report saved to: validation-report.json")
        print("="*60)
        
        return len(self.errors) == 0
    
    def _generate_recommendations(self) -> List[str]:
        """Generate setup recommendations"""
        recommendations = []
        
        if len(self.errors) > 0:
            recommendations.append("Fix critical errors before proceeding")
        
        if len(self.warnings) > 0:
            recommendations.append("Review warnings for potential improvements")
        
        # Always include these recommendations
        recommendations.extend([
            "Set production environment variables in .env.prod",
            "Configure external API credentials",
            "Run comprehensive tests: python -m pytest tests/ -v",
            "Validate with development server: cd src && python main.py --web",
            "Consider setting up Redis for caching in production",
            "Review security settings before deployment"
        ])
        
        return recommendations

def main():
    """Main validation entry point"""
    validator = SetupValidator()
    
    if validator.run_validation():
        print("\n🎉 All validations passed! Project is ready.")
        return 0
    else:
        print("\n⚠️  Some validations failed. Review the report for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())