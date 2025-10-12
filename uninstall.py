#!/usr/bin/env python3
"""
Uninstall script for Web Explorer MCP
Removes all Docker containers, volumes, and cleans up the project
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command,
            check=check,
            capture_output=True,
            text=True,
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command)}")
        print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def main():
    """Main uninstallation routine."""
    print("=" * 50)
    print("Web Explorer MCP Uninstaller")
    print("=" * 50)
    print()

    # Confirm uninstallation
    response = input(
        "This will remove all Docker containers and volumes. Continue? [y/N]: "
    )
    if response.lower() not in ["y", "yes"]:
        print("Uninstallation cancelled.")
        sys.exit(0)

    # Get the project directory
    project_dir = Path(__file__).parent.resolve()
    os.chdir(project_dir)

    # Stop and remove Docker containers
    print("\n1. Stopping and removing Docker containers (SearxNG + Playwright)...")
    result = run_command(["docker", "compose", "down", "-v"], check=False)
    if result.returncode == 0:
        print("✓ Docker containers and volumes removed")
    else:
        print("⚠ Warning: Failed to remove Docker containers")
        print("  You may need to run: docker compose down -v")

    # Check for uvx cache
    print("\n2. Checking for uvx cache...")
    print("ℹ uvx automatically manages temporary environments")
    print("  No manual cleanup needed for uvx installations")

    # Remove local Python environment
    venv_dir = project_dir / ".venv"
    if venv_dir.exists():
        print("\n3. Removing local Python virtual environment...")
        try:
            import shutil

            shutil.rmtree(venv_dir)
            print("✓ Virtual environment removed")
        except Exception as e:
            print(f"⚠ Warning: Failed to remove virtual environment: {e}")
            print(f"  You may need to manually remove: {venv_dir}")
    else:
        print("\n3. No local virtual environment found")

    print("\n" + "=" * 50)
    print("Uninstallation Complete!")
    print("=" * 50)
    print()
    print("Docker services (SearxNG + Playwright) have been stopped and removed.")
    print()
    print("To completely remove the project:")
    print("  cd ..")
    print(f"  rm -rf {project_dir.name}")
    print()
    print("Note: uvx temporary environments are automatically cleaned up.")
    print()


if __name__ == "__main__":
    main()
