#!/usr/bin/env python3
"""
FortiGate Project CLI Management Tool
Unified command-line interface for project operations
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd_list, description):
    """Run a command with proper error handling"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd_list, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def init_project():
    """Initialize project setup"""
    print("🚀 Initializing FortiGate project...")
    return run_command([sys.executable, "init-project.py"], "Project initialization")

def validate_setup():
    """Validate project setup"""
    print("🔍 Validating project setup...")
    return run_command([sys.executable, "validate-setup.py"], "Setup validation")

def start_dev():
    """Start development server"""
    print("🖥️  Starting development server...")
    print("   Server will be available at: http://localhost:7777")
    print("   Press Ctrl+C to stop the server")
    return run_command([sys.executable, "start-dev.py"], "Development server")

def run_tests():
    """Run project tests"""
    print("🧪 Running project tests...")
    test_commands = [
        ([sys.executable, "-m", "pytest", "tests/", "-v"], "Unit tests"),
        ([sys.executable, "test_fortigate_api.py"], "API tests"),
        ([sys.executable, "-m", "pytest", "tests/functional/", "-v"], "Functional tests")
    ]
    
    all_passed = True
    for cmd, desc in test_commands:
        if Path(cmd[-1]).exists() or "pytest" in cmd:
            if not run_command(cmd, desc):
                all_passed = False
        else:
            print(f"⏭️  Skipping {desc} (file not found)")
    
    return all_passed

def show_status():
    """Show project status"""
    print("📊 FortiGate Project Status")
    print("="*40)
    
    # Check critical files
    critical_files = [
        (".env.dev", "Development environment"),
        (".env.prod", "Production environment"),
        ("mcp-tools-config.json", "MCP tools configuration"),
        ("agent-config.json", "Agent configuration"),
        ("src/main.py", "Main application"),
        ("requirements.txt", "Dependencies")
    ]
    
    for file_path, description in critical_files:
        status = "✅" if Path(file_path).exists() else "❌"
        print(f"  {status} {description}")
    
    # Check if server is running
    try:
        import requests
        response = requests.get("http://localhost:7777/api/health", timeout=2)
        if response.status_code == 200:
            print("  ✅ Development server is running")
        else:
            print("  ❌ Development server not responding")
    except:
        print("  ⏸️  Development server not running")
    
    print("\n🔧 Available Commands:")
    print("  python3 fortinet-cli.py init       # Initialize project")
    print("  python3 fortinet-cli.py validate   # Validate setup")
    print("  python3 fortinet-cli.py dev        # Start dev server")
    print("  python3 fortinet-cli.py test       # Run tests")
    print("  python3 fortinet-cli.py status     # Show this status")

def show_help():
    """Show help information"""
    print("🎯 FortiGate Project CLI")
    print("="*30)
    print("Available commands:")
    print("  init     - Initialize project setup")
    print("  validate - Validate project configuration")
    print("  dev      - Start development server")
    print("  test     - Run project tests")
    print("  status   - Show project status")
    print("  help     - Show this help")
    print("\nExamples:")
    print("  python3 fortinet-cli.py init")
    print("  python3 fortinet-cli.py dev")
    print("  python3 fortinet-cli.py test")

def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        show_status()
        return 0
    
    command = sys.argv[1].lower()
    
    commands = {
        "init": init_project,
        "initialize": init_project,
        "validate": validate_setup,
        "check": validate_setup,
        "dev": start_dev,
        "start": start_dev,
        "serve": start_dev,
        "test": run_tests,
        "tests": run_tests,
        "status": show_status,
        "help": show_help,
        "--help": show_help,
        "-h": show_help
    }
    
    if command in commands:
        try:
            success = commands[command]()
            return 0 if success else 1
        except KeyboardInterrupt:
            print("\n🛑 Operation cancelled by user")
            return 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python3 fortinet-cli.py help' for available commands")
        return 1

if __name__ == "__main__":
    sys.exit(main())