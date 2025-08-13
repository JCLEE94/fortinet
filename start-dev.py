#!/usr/bin/env python3
"""
FortiGate Development Server Startup Script
Quick development environment launcher
"""

import os
import sys
import subprocess
from pathlib import Path

def load_dev_environment():
    """Load development environment variables"""
    env_file = Path(".env.dev")
    if env_file.exists():
        print("📁 Loading development environment...")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value
        print("✅ Development environment loaded")
    else:
        print("⚠️  .env.dev not found, using default settings")

def start_dev_server():
    """Start the development server"""
    print("🚀 Starting FortiGate development server...")
    print("📍 Server will be available at: http://localhost:7777")
    print("🔧 Mode: Development (Mock services enabled)")
    print("📋 Health check: http://localhost:7777/api/health")
    print("\n" + "="*50)
    
    # Change to src directory and start the server
    os.chdir("src")
    subprocess.run([sys.executable, "main.py", "--web"])

def main():
    """Main entry point"""
    print("🎯 FortiGate Development Server")
    print("="*40)
    
    # Check if we're in the right directory
    if not Path("src/main.py").exists():
        print("❌ Error: src/main.py not found")
        print("   Please run this script from the project root directory")
        return 1
    
    try:
        load_dev_environment()
        start_dev_server()
        return 0
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())