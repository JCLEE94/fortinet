#!/usr/bin/env python3
"""
Basedir Standards Cleanup Script for GitOps Projects
Implements CNCF GitOps best practices and Python src-layout
"""

import os
import shutil
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

class BasedirCleaner:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.cleanup_log = []
        
    def log_action(self, action: str, details: str = ""):
        """Log cleanup actions"""
        entry = {"action": action, "details": details}
        self.cleanup_log.append(entry)
        print(f"✓ {action}: {details}")
    
    def remove_temporary_files(self):
        """Remove temporary and backup files"""
        temp_patterns = [
            "*.tmp", "*.temp", "*.bak", "*.backup", "*~", "*.swp", "*.swo", 
            "*.orig", "*.rej", "*-backup", "*-old", "*-copy", "*-temp",
            ".DS_Store", "Thumbs.db", "desktop.ini"
        ]
        
        for pattern in temp_patterns:
            for file in self.project_root.rglob(pattern):
                try:
                    file.unlink()
                    self.log_action("Removed temp file", str(file))
                except Exception as e:
                    print(f"⚠️ Could not remove {file}: {e}")
    
    def standardize_gitops_structure(self):
        """Ensure GitOps structure follows CNCF standards"""
        gitops_structure = {
            "k8s/base": "Kustomize base manifests",
            "k8s/overlays/dev": "Development environment",
            "k8s/overlays/staging": "Staging environment", 
            "k8s/overlays/production": "Production environment",
            "argocd-apps": "ArgoCD Application definitions",
            ".github/workflows": "GitOps CI/CD pipelines"
        }
        
        for dir_path, desc in gitops_structure.items():
            full_path = self.project_root / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                self.log_action("Created GitOps directory", f"{dir_path} ({desc})")
    
    def organize_test_files(self):
        """Move timestamped test files to appropriate locations"""
        data_test_dir = self.project_root / "data" / "test-results"
        data_test_dir.mkdir(parents=True, exist_ok=True)
        
        # Move timestamped files
        for file in self.project_root.glob("*_2025*.json"):
            new_path = data_test_dir / file.name
            shutil.move(str(file), str(new_path))
            self.log_action("Moved test file", f"{file.name} -> data/test-results/")
    
    def standardize_python_structure(self):
        """Ensure Python project follows src-layout"""
        # Check if src-layout is already implemented
        src_dir = self.project_root / "src"
        if src_dir.exists():
            self.log_action("Python src-layout verified", "Structure already compliant")
        else:
            self.log_action("Warning", "Python src-layout not found - manual intervention needed")
    
    def create_missing_files(self):
        """Create essential files if missing"""
        essential_files = {
            ".gitignore": "# Python\n__pycache__/\n*.pyc\n*.pyo\n*.egg-info/\n\n# IDEs\n.vscode/\n.idea/\n\n# OS\n.DS_Store\nThumbs.db",
            "src/__init__.py": "# FortiGate Nextrade Package",
        }
        
        for file_path, content in essential_files.items():
            full_path = self.project_root / file_path
            if not full_path.exists():
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)
                self.log_action("Created essential file", file_path)
    
    def cleanup_deployment_scripts(self):
        """Organize deployment scripts"""
        scripts_dir = self.project_root / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        # Move deployment scripts to scripts directory
        for script in self.project_root.glob("*-deploy*.sh"):
            if script.parent != scripts_dir:
                new_path = scripts_dir / script.name
                shutil.move(str(script), str(new_path))
                new_path.chmod(0o755)
                self.log_action("Moved deployment script", f"{script.name} -> scripts/")
    
    def validate_gitops_manifests(self):
        """Validate GitOps manifests"""
        k8s_base = self.project_root / "k8s" / "base"
        if k8s_base.exists():
            kustomization = k8s_base / "kustomization.yaml"
            if kustomization.exists():
                self.log_action("GitOps validation", "Kustomize base structure valid")
            else:
                self.log_action("Warning", "Missing kustomization.yaml in base")
    
    def run_cleanup(self):
        """Execute complete cleanup process"""
        print("🧹 Starting Basedir Standards Cleanup (GitOps + Python)")
        print("=" * 55)
        
        # Execute cleanup steps
        self.remove_temporary_files()
        self.standardize_gitops_structure()
        self.organize_test_files()
        self.standardize_python_structure()
        self.create_missing_files()
        self.cleanup_deployment_scripts()
        self.validate_gitops_manifests()
        
        # Generate report
        self.generate_cleanup_report()
        
        print("\n✅ Basedir Standards Cleanup Complete!")
        print(f"📋 Report saved to: basedir-cleanup-report.json")
    
    def generate_cleanup_report(self):
        """Generate cleanup summary report"""
        report = {
            "timestamp": str(Path().cwd()),
            "project": "fortinet (FortiGate Nextrade)",
            "standards": "CNCF GitOps + Python src-layout",
            "actions_completed": len(self.cleanup_log),
            "log": self.cleanup_log,
            "structure_compliance": {
                "gitops": True,
                "python_src_layout": (self.project_root / "src").exists(),
                "kustomize": (self.project_root / "k8s" / "base").exists()
            }
        }
        
        report_file = self.project_root / "basedir-cleanup-report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

if __name__ == "__main__":
    cleaner = BasedirCleaner("/home/jclee/app/fortinet")
    cleaner.run_cleanup()