#!/usr/bin/env python3
"""
Quick test runner for development.
Runs a subset of tests for faster feedback during development.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run command and return result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def main():
    """Run quick tests."""
    print("🚀 SarkariBot Quick Test Runner")
    print("===============================")
    
    # Get repository root
    repo_root = Path(__file__).parent.parent
    backend_dir = repo_root / "sarkaribot" / "backend"
    frontend_dir = repo_root / "sarkaribot" / "frontend"
    
    # Set environment
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.testing"
    os.environ["PYTHONPATH"] = str(backend_dir)
    
    print("📋 Running Django system checks...")
    success, output = run_command("python manage.py check", cwd=backend_dir)
    if not success:
        print(f"❌ Django checks failed:\n{output}")
        return 1
    print("✅ Django checks passed")
    
    print("\n🧪 Running quick backend tests...")
    test_cmd = "pytest tests/test_models_jobs.py::TestJobCategory -v --tb=short"
    success, output = run_command(test_cmd, cwd=backend_dir)
    if not success:
        print(f"❌ Backend tests failed:\n{output}")
        return 1
    print("✅ Quick backend tests passed")
    
    print("\n🎨 Running frontend linting...")
    success, output = run_command("npm run lint", cwd=frontend_dir)
    if not success:
        print(f"⚠️  Frontend linting issues:\n{output}")
        # Don't fail on linting issues, just warn
    else:
        print("✅ Frontend linting passed")
    
    print("\n🧪 Running quick frontend tests...")
    test_cmd = "npm test -- --testPathPattern=JobCard.test.js --watchAll=false"
    success, output = run_command(test_cmd, cwd=frontend_dir)
    if not success:
        print(f"❌ Frontend tests failed:\n{output}")
        return 1
    print("✅ Quick frontend tests passed")
    
    print("\n🎉 All quick tests passed!")
    print("\nFor full test coverage, run: ./scripts/run_tests.sh")
    return 0

if __name__ == "__main__":
    sys.exit(main())